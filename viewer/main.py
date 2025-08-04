from fastapi import FastAPI, HTTPException
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
import logging

app = FastAPI()

# Włącz maksymalne logowanie
logging.basicConfig(level=logging.DEBUG)

STORAGE_ACCOUNT_NAME = "storappsdevasd213"
TABLE_NAME = "email"

storage_url = f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net"
logging.debug(f"Storage URL: {storage_url}")

credential = DefaultAzureCredential()

try:
    token = credential.get_token("https://storage.azure.com/.default")
    logging.debug(f"Access token acquired successfully: {token.token[:10]}...")
except Exception as e:
    logging.error(f"Failed to acquire token: {e}")
    raise RuntimeError(f"Credential error: {e}")

table_service = TableServiceClient(endpoint=storage_url, credential=credential)
table_client = table_service.get_table_client(TABLE_NAME)

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
