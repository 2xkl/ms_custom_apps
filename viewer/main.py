# from fastapi import FastAPI, HTTPException
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
import logging

from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "ok"}

# @app.get("/emails")
# def get_all_emails():
#     try:
#         logging.info("Fetching emails from Table Storage...")
#         # Poprawiony filtr PartitionKey na 'email'
#         entities = table_client.query_entities("PartitionKey eq 'email'")
#         result = []

#         for entity in entities:
#             logging.debug(f"Entity found: {entity}")
#             result.append({
#                 "sender": entity.get("sender"),
#                 "message": entity.get("message"),
#                 "type": entity.get("type"),
#                 "score": entity.get("score"),
#                 "reason": entity.get("reason"),
#                 "timestamp": entity.get("timestamp"),
#                 "rowKey": entity.get("RowKey"),
#             })

#         return {"items": result}

#     except Exception as e:
#         logging.exception("Failed to fetch from Table Storage.")
#         raise HTTPException(status_code=500, detail=str(e))
