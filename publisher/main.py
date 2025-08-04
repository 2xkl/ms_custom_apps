from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import json

app = FastAPI()

SERVICEBUS_CONNECTION_STR = os.getenv("SERVICEBUS_CONNECTION_STR")
TOPIC_NAME = os.getenv("SERVICEBUS_TOPIC_NAME")

if not SERVICEBUS_CONNECTION_STR or not TOPIC_NAME:
    raise RuntimeError("Missing SERVICEBUS_CONNECTION_STR or SERVICEBUS_TOPIC_NAME environment variables")

class Payload(BaseModel):
    sender: str
    message: str

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/publish")
async def publish_message(payload: Payload):
    try:
        with ServiceBusClient.from_connection_string(SERVICEBUS_CONNECTION_STR) as client:
            sender = client.get_topic_sender(topic_name=TOPIC_NAME)
            with sender:
                body = json.dumps(payload.dict())
                msg = ServiceBusMessage(body)
                sender.send_messages(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

    return {"status": "sent"}
