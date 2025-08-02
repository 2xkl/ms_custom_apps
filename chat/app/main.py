import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import AzureOpenAI
from fastapi.middleware.cors import CORSMiddleware

subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

class ChatRequest(BaseModel):
    message: str

chat_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    chat_history.append({"role": "user", "content": request.message})
    
    response = client.chat.completions.create(
        model=deployment,
        messages=chat_history,
    )
    
    assistant_message = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": assistant_message})
    
    return {"response": assistant_message}
