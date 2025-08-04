from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

SERVICE_BUS_NAMESPACE = os.getenv("SERVICEBUS_NAMESPACE")
TOPIC_NAME = os.getenv("SERVICEBUS_TOPIC_NAME", "events")

if not SERVICE_BUS_NAMESPACE:
    raise RuntimeError("Missing SERVICEBUS_NAMESPACE environment variable.")

credential = DefaultAzureCredential()
bus_client = ServiceBusClient(fully_qualified_namespace=SERVICE_BUS_NAMESPACE, credential=credential)

class Payload(BaseModel):
    sender: str
    message: str

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/message")
async def publish_message(payload: Payload, request: Request):
    try:
        logging.info(f"Received message from {payload.sender}")

        message = {
            "sender": payload.sender,
            "message": payload.message,
            "source_ip": request.client.host,
        }

        # Send to topic
        with bus_client:
            sender = bus_client.get_topic_sender(topic_name=TOPIC_NAME)
            with sender:
                sb_message = ServiceBusMessage(str(message))
                sender.send_messages(sb_message)

        return {"status": "sent", "details": message}

    except Exception as e:
        logging.exception("Failed to publish message")
        raise HTTPException(status_code=500, detail=str(e))
