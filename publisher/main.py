from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os
import logging
import json

app = FastAPI()
logging.basicConfig(level=logging.INFO)

SERVICE_BUS_NAMESPACE = os.getenv("SERVICEBUS_NAMESPACE")
TOPIC_NAME = os.getenv("SERVICEBUS_TOPIC_NAME", "events")

if not SERVICE_BUS_NAMESPACE:
    raise RuntimeError("Missing SERVICEBUS_NAMESPACE environment variable.")

credential = DefaultAzureCredential()
bus_client = ServiceBusClient(
    fully_qualified_namespace=SERVICE_BUS_NAMESPACE,
    credential=credential
)

class Payload(BaseModel):
    sender: str
    message: str

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/message")
async def publish_message(payload: Payload):
    try:
        logging.info(f"Publishing message from: {payload.sender}")

        body = json.dumps(payload.dict())

        with bus_client:
            sender = bus_client.get_topic_sender(topic_name=TOPIC_NAME)
            with sender:
                sb_message = ServiceBusMessage(body)
                sender.send_messages(sb_message)

        return {"status": "sent"}

    except Exception as e:
        logging.exception("Failed to send message")
        raise HTTPException(status_code=500, detail=str(e))
