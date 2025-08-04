import os
import json
import logging
import requests
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.data.tables import TableServiceClient
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)

# Config from environment
SERVICE_BUS_NAMESPACE = os.getenv("SERVICEBUS_NAMESPACE")
TOPIC_NAME = os.getenv("SERVICEBUS_TOPIC_NAME", "events")
SUBSCRIPTION_NAME = os.getenv("SERVICEBUS_SUBSCRIPTION_NAME", "mails")
INSPECTOR_URL = os.getenv("INSPECTOR_URL", "http://10.1.2.4")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
TABLE_NAME = os.getenv("TABLE_NAME", "email")

# Validations
for var_name in ["SERVICEBUS_NAMESPACE", "STORAGE_ACCOUNT_NAME"]:
    if not os.getenv(var_name):
        raise RuntimeError(f"Missing environment variable: {var_name}")

# Auth
credential = DefaultAzureCredential()

# Clients
bus_client = ServiceBusClient(
    fully_qualified_namespace=SERVICE_BUS_NAMESPACE,
    credential=credential
)

storage_url = f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net"
table_service = TableServiceClient(endpoint=storage_url, credential=credential)
table_client = table_service.get_table_client(TABLE_NAME)

def inspect_and_store(message_body: dict):
    try:
        response = requests.post(INSPECTOR_URL, json=message_body)
        response.raise_for_status()
        result = response.json()

        logging.info(f"Received inspection result: {result}")

        row = {
            "PartitionKey": "emails",
            "RowKey": str(uuid.uuid4()),
            "sender": message_body.get("sender"),
            "message": message_body.get("message"),
            "type": result.get("type"),
            "score": result.get("score"),
            "reason": result.get("reason"),
            "timestamp": datetime.utcnow().isoformat()
        }

        table_client.create_entity(entity=row)
        logging.info("Inserted row into Table Storage")

    except Exception as e:
        logging.exception(f"Failed to process message: {e}")

def main():
    logging.info("Receiver started. Waiting for messages...")

    with bus_client:
        receiver = bus_client.get_subscription_receiver(
            topic_name=TOPIC_NAME,
            subscription_name=SUBSCRIPTION_NAME
        )
        with receiver:
            for msg in receiver:
                try:
                    body = json.loads(str(msg))
                    logging.info(f"Received message: {body}")
                    inspect_and_store(body)
                    receiver.complete_message(msg)
                except Exception as e:
                    logging.exception("Failed to handle message")
                    receiver.abandon_message(msg)

if __name__ == "__main__":
    main()
