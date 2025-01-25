from typing import Protocol, List, Dict, Any
from pymongo import MongoClient

# Define a protocol for database interaction
class Database(Protocol):
    def connect(self) -> None:
        """Connect to the database."""
        pass

    def get_customers_services(self) -> List[Dict[str, Any]]:
        """Fetch all services for customers."""
        pass

# MongoDB implementation
class MongoDB(Database):
    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: MongoClient | None = None
        self.db: Any = None

    def connect(self) -> None:
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.database_name]

    def get_customers_services(self) -> List[Dict[str, Any]]:
        customers = self.db["customers"]
        return [
            {"customer_id": customer["_id"], "services": customer.get("services", [])}
            for customer in customers.find()
        ]

# Main function to use any database implementation
def main(database: Database):
    database.connect()
    services = database.get_customers_services()
    for service in services:
        print(service)


if __name__ == "__main__":
    # Example usage with MongoDB
    mongo_db = MongoDB("mongodb://localhost:27017", "mydatabase")
    main(mongo_db)
