from fastapi import FastAPI, HTTPException
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from datetime import datetime
import os
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Environment variable must contain the full table storage account name (e.g., "myaccount.table.core.windows.net")
TABLE_STORAGE_ACCOUNT_URL = os.getenv("TABLE_STORAGE_ACCOUNT_URL")  # e.g., https://youraccount.table.core.windows.net
TABLE_NAME = os.getenv("TABLE_NAME", "emails")

if not TABLE_STORAGE_ACCOUNT_URL:
    raise RuntimeError("Missing TABLE_STORAGE_ACCOUNT_URL environment variable.")

# Use DefaultAzureCredential (supports workload identity in AKS)
credential = DefaultAzureCredential()
table_service_client = TableServiceClient(endpoint=TABLE_STORAGE_ACCOUNT_URL, credential=credential)
table_client = table_service_client.get_table_client(table_name=TABLE_NAME)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/emails")
def get_all_emails():
    try:
        logging.info("Fetching emails from Table Storage...")
        entities = table_client.query_entities("PartitionKey eq 'emails'")
        result = []

        for entity in entities:
            result.append({
                "sender": entity.get("sender"),
                "message": entity.get("message"),
                "type": entity.get("type"),
                "score": entity.get("score"),
                "reason": entity.get("reason"),
                "timestamp": entity.get("timestamp"),
                "rowKey": entity.get("RowKey"),
            })

        return {"items": result}

    except Exception as e:
        logging.exception("Failed to fetch from Table Storage.")
        raise HTTPException(status_code=500, detail=str(e))
