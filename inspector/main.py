from fastapi import FastAPI
from pydantic import BaseModel
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
import json

# Konfiguracja Key Vault
key_vault_name = os.getenv("AZURE_KEYVAULT_NAME")  # np. zdefiniowane jako zmienna środowiskowa lub przez ConfigMap
kv_uri = f"https://{key_vault_name}.vault.azure.net"

# Autoryzacja za pomocą workload identity
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=kv_uri, credential=credential)

# Pobierz dane z Key Vault
subscription_key = secret_client.get_secret("OAIKEY").value
endpoint = secret_client.get_secret("OAIENDPOINT").value
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Zakładamy, że deployment jest stały i ustawiony jako env
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")  # Można też wrzucić do KV

# Inicjalizacja klienta OpenAI
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# FastAPI app
app = FastAPI()

class InspectRequest(BaseModel):
    sender: str
    message: str

class InspectResponse(BaseModel):
    type: str 
    score: float
    reason: str

async def classify_email(sender: str, message: str) -> InspectResponse:
    system_prompt = """You are an AI email security inspector. Your task is to classify the message as 'normal', 'spam', or 'fraud'.
For each message, return:
- type: one of ['normal', 'spam', 'fraud']
- score: a number between 0.0 and 1.0 (confidence level of the classification)
- reason: a one-sentence explanation

Example response in JSON format:
{ "type": "spam", "score": 0.85, "reason": "Contains phrases typical of spam" }
"""
    user_message = f"Sender: {sender}\nMessage content:\n{message}\n\nPlease evaluate this message."

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        return InspectResponse(
            type=parsed["type"],
            score=parsed["score"],
            reason=parsed["reason"]
        )
    except Exception as e:
        return InspectResponse(
            type="unknown",
            score=0.0,
            reason=f"Failed to parse response: {str(e)}. Raw content: {content}"
        )

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/inspect", response_model=InspectResponse)
async def inspect(request: InspectRequest):
    return await classify_email(request.sender, request.message)
