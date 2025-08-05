import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
from fastapi.middleware.cors import CORSMiddleware
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

key_vault_name = os.getenv("AZURE_KEYVAULT_NAME")
if not key_vault_name:
    raise RuntimeError("AZURE_KEYVAULT_NAME environment variable is not set")

vault_uri = f"https://{key_vault_name}.vault.azure.net"

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=vault_uri, credential=credential)

try:
    subscription_key = secret_client.get_secret("OAIKEY").value
    endpoint = secret_client.get_secret("OAIENDPOINT").value
except Exception as e:
    raise RuntimeError(f"Failed to retrieve secrets from Key Vault: {str(e)}")

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
if not deployment:
    raise RuntimeError("AZURE_OPENAI_DEPLOYMENT env var must be set")

api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
client_ui_url = os.getenv("CLIENT_URL")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[client_ui_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    chat_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": request.message}
    ]

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=chat_history,
        )
        assistant_message = response.choices[0].message.content
        return ChatResponse(response=assistant_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI request failed: {str(e)}")
