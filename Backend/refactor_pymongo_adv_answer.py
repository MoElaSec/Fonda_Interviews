from typing import Protocol, Any, Union, cast
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
import asyncpg
from asyncpg.pool import Pool as AsyncpgPool


# -----------------------------------------
# 1) Define Custom Pydantic Models
# -----------------------------------------


class PyObjectId(ObjectId):
    """A custom type to handle MongoDB ObjectId in Pydantic models."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)


class ServiceModel(BaseModel):
    """Example service model that you might store in 'services'."""

    name: str
    description: str | None = None


class CustomerModel(BaseModel):
    """A more complete Customer model."""

    id: Union[PyObjectId, int] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    services: list[ServiceModel] = Field(default_factory=list)

    class Config:
        # Allow alias (“_id”) so we don’t have to rename it in the DB
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class PaginatedResponse(BaseModel):
    """Generic offset-based pagination response."""

    data: list[CustomerModel]
    page: int
    page_size: int
    total_count: int
    total_pages: int


class CursorPaginatedResponse(BaseModel):
    """Generic cursor-based pagination response."""

    data: list[CustomerModel]
    next_cursor: Union[str, int] | None = None  # Cursor can be ObjectId (str) or int
    has_more: bool


# -----------------------------------------
# 2) Database Protocol
# -----------------------------------------


class Database(Protocol):
    """Interface for database operations."""

    async def connect(self) -> None:
        """Connect to the database."""
        ...

    async def get_customers_services(
        self, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse:
        """Fetch all services for customers with offset-based pagination."""
        ...

    async def get_customers_services_cursor_pagination(
        self, limit: int = 10, cursor: Union[str, int] | None = None
    ) -> CursorPaginatedResponse:
        """Fetch all services for customers with cursor-based pagination."""
        ...


# -----------------------------------------
# 3) MongoDB Implementation
# -----------------------------------------


class MongoDB(Database):
    """MongoDB implementation using Motor for async operations."""

    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase[Any] | None = None

    async def connect(self) -> None:
        """Initialize the AsyncIOMotorClient and database reference."""
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database_name]

    async def get_customers_services(
        self, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse:
        """Retrieve customers with offset-based pagination, returning services data."""
        if not self.db:
            raise RuntimeError("Database is not connected. Call connect() first.")

        customers_collection = self.db["customers"]

        # Calculate pagination skip and retrieve documents
        skip = (page - 1) * page_size

        # Count total documents for pagination math
        total_count = await customers_collection.count_documents({})

        cursor = customers_collection.find({}).skip(skip).limit(page_size)
        docs = await cursor.to_list(length=page_size)

        # Convert the raw docs into typed Pydantic models
        customers = [CustomerModel(**doc) for doc in docs]

        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

        return PaginatedResponse(
            data=customers,
            page=page,
            page_size=page_size,
            total_count=total_count,
            total_pages=total_pages,
        )

    async def get_customers_services_cursor_pagination(
        self, limit: int = 10, cursor: Union[str, int] | None = None
    ) -> CursorPaginatedResponse:
        """Retrieve customers with cursor-based pagination, returning services data."""
        if not self.db:
            raise RuntimeError("Database is not connected. Call connect() first.")

        customers_collection = self.db["customers"]

        query = {}
        sort = [("_id", 1)]  # Sort by _id ascending

        if cursor:
            if not isinstance(cursor, str):
                raise ValueError(
                    "Invalid cursor for MongoDB. Must be a valid ObjectId string."
                )
            try:
                last_id = ObjectId(cursor)
                query["_id"] = {"$gt": last_id}
            except Exception:
                raise ValueError(
                    "Invalid cursor for MongoDB. Must be a valid ObjectId string."
                )

        cursor_query = (
            customers_collection.find(query)
            .sort(sort)
            .limit(limit + 1)  # Fetch one extra to check if there's a next page
        )

        docs = await cursor_query.to_list(length=limit + 1)

        has_more = len(docs) > limit
        customers = [CustomerModel(**doc) for doc in docs[:limit]]

        # Safely extract next_cursor
        next_cursor: Union[str, int] | None = (
            str(customers[-1].id) if has_more else None
        )

        return CursorPaginatedResponse(
            data=customers, next_cursor=next_cursor, has_more=has_more
        )


# -----------------------------------------
# 4) PostgreSQL Implementation
# -----------------------------------------


class PostgreSQL(Database):
    """PostgreSQL implementation using asyncpg for async operations."""

    def __init__(self, dsn: str, min_size: int = 10, max_size: int = 10):
        self.dsn = dsn
        self.pool: AsyncpgPool | None = None
        self.min_size = min_size
        self.max_size = max_size

    async def connect(self) -> None:
        """Initialize the asyncpg connection pool."""
        self.pool = await asyncpg.create_pool(
            dsn=self.dsn, min_size=self.min_size, max_size=self.max_size
        )

    async def get_customers_services(
        self, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse:
        """Retrieve customers with offset-based pagination, returning services data."""
        if not self.pool:
            raise RuntimeError("Database is not connected. Call connect() first.")

        offset = (page - 1) * page_size

        async with self.pool.acquire() as connection:
            total_count = await connection.fetchval("SELECT COUNT(*) FROM customers;")

            query = """
                SELECT id, name, services
                FROM customers
                ORDER BY id ASC
                OFFSET $1
                LIMIT $2
            """
            rows = await connection.fetch(query, offset, page_size)
            customers = [
                CustomerModel(
                    _id=row["id"],
                    name=row["name"],
                    services=[ServiceModel(**s) for s in row["services"]],
                )
                for row in rows
            ]

            total_pages = (
                (total_count + page_size - 1) // page_size if page_size > 0 else 1
            )

            return PaginatedResponse(
                data=customers,
                page=page,
                page_size=page_size,
                total_count=total_count,
                total_pages=total_pages,
            )

    async def get_customers_services_cursor_pagination(
        self, limit: int = 10, cursor: Union[str, int] | None = None
    ) -> CursorPaginatedResponse:
        """Retrieve customers with cursor-based pagination, returning services data."""
        if not self.pool:
            raise RuntimeError("Database is not connected. Call connect() first.")

        # Ensure cursor is an integer for PostgreSQL
        if cursor is not None and not isinstance(cursor, int):
            raise ValueError("Invalid cursor for PostgreSQL. Must be an integer.")

        async with self.pool.acquire() as connection:
            # If cursor is provided, fetch records with id > cursor
            if cursor is not None:
                query = """
                    SELECT id, name, services
                    FROM customers
                    WHERE id > $1
                    ORDER BY id ASC
                    LIMIT $2
                """
                rows = await connection.fetch(query, cursor, limit + 1)
            else:
                # If no cursor, start from the beginning
                query = """
                    SELECT id, name, services
                    FROM customers
                    ORDER BY id ASC
                    LIMIT $1
                """
                rows = await connection.fetch(query, limit + 1)

            has_more = len(rows) > limit
            customers = [
                CustomerModel(
                    _id=row["id"],
                    name=row["name"],
                    services=[ServiceModel(**s) for s in row["services"]],
                )
                for row in rows[:limit]
            ]

            next_cursor: Union[str, int] | None = (
                cast(int, customers[-1].id) if has_more else None
            )

            return CursorPaginatedResponse(
                data=customers, next_cursor=next_cursor, has_more=has_more
            )

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()


# -----------------------------------------
# 5) Unit of Work (UoW) Pattern
# -----------------------------------------


class UnitOfWork:
    """
    Context manager to ensure database connections are opened and cleaned up.
    """

    def __init__(self, database: Database):
        self.database = database

    async def __aenter__(self) -> Database:
        await self.database.connect()
        return self.database

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Close connections based on the database type
        if isinstance(self.database, MongoDB) and self.database.client:
            self.database.client.close()
        elif isinstance(self.database, PostgreSQL) and self.database.pool:
            await self.database.close()


# -----------------------------------------
# 6) Main Usage
# -----------------------------------------


async def main(database: Database, use_cursor_pagination: bool = False):
    """
    Example usage of our UoW with the Database implementation.

    Args:
        database: An instance of a class that adheres to the Database protocol.
        use_cursor_pagination: Whether to use cursor-based pagination. Defaults to False.
    """
    async with UnitOfWork(database) as db:
        if use_cursor_pagination:
            # Example cursor-based pagination
            cursor: Union[str, int] | None = (
                None  # Initialize cursor to None for the first page
            )
            while True:
                paginated_result: CursorPaginatedResponse = (
                    await db.get_customers_services_cursor_pagination(
                        limit=5, cursor=cursor
                    )
                )

                print("Pagination Info:")
                print(f" Next Cursor: {paginated_result.next_cursor}")
                print(f" Has More: {paginated_result.has_more}")
                print("\nCustomers:")
                for customer in paginated_result.data:
                    print(customer.dict(by_alias=True))

                if not paginated_result.has_more:
                    break  # Exit the loop if there are no more records

                cursor = paginated_result.next_cursor  # Set cursor for the next page
        else:
            # Example offset-based pagination
            paginated_result: PaginatedResponse = await db.get_customers_services(
                page=1, page_size=5
            )

            print("Pagination Info:")
            if isinstance(paginated_result, PaginatedResponse):
                print(f" Page: {paginated_result.page}")
                print(f" Page Size: {paginated_result.page_size}")
                print(f" Total Count: {paginated_result.total_count}")
                print(f" Total Pages: {paginated_result.total_pages}")
            else:
                print("Invalid response type.")
            print("\nCustomers:")
            for customer in paginated_result.data:
                print(customer.dict(by_alias=True))


# -----------------------------------------
# 7) Entry Point
# -----------------------------------------


if __name__ == "__main__":
    import asyncio

    async def run_mongodb_example():
        print("---- MongoDB Example: Offset-Based Pagination ----")
        # Create an instance of MongoDB
        mongo_db = MongoDB("mongodb://localhost:27017", "mydatabase")
        await main(mongo_db, use_cursor_pagination=False)

        print("\n---- MongoDB Example: Cursor-Based Pagination ----")
        await main(mongo_db, use_cursor_pagination=True)

    async def run_postgresql_example():
        print("\n---- PostgreSQL Example: Offset-Based Pagination ----")
        # Create an instance of PostgreSQL
        postgres_db = PostgreSQL(
            dsn="postgresql://user:password@localhost:5432/mydatabase"
        )
        await main(postgres_db, use_cursor_pagination=False)

        print("\n---- PostgreSQL Example: Cursor-Based Pagination ----")
        await main(postgres_db, use_cursor_pagination=True)

    # Run both examples sequentially
    async def run_examples():
        await run_mongodb_example()
        await run_postgresql_example()

    asyncio.run(run_examples())
