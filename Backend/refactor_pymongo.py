from pymongo import MongoClient


def get_customer_services():
    client = MongoClient("mongodb://localhost:27017")
    db = client["mydatabase"]

    customers_collection = db["customers"]

    customer_services = []
    for customer in customers_collection.find():
        customer_services.append(
            {"customer_id": customer["_id"], "services": customer.get("services", [])}
        )

    client.close()

    return customer_services


if __name__ == "__main__":
    services = get_customer_services()
    for service in services:
        print(service)
