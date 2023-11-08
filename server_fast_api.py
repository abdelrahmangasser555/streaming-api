from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents import get_agent, Agent
from agent_generator import *
import time
import asyncio
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = "ls__fa867f0c19af4047a350a137490a262a"
# os.environ["LANGCHAIN_PROJECT"] = "test"

app = FastAPI()

# enable CORS FOR ALL ORIGINS *
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # allow credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_data():
    for i in range(5):
        time.sleep(1)  # Simulating some processing delay
        yield f"Data {i}\n"


async def generate_data_async():
    for i in range(5):
        await asyncio.sleep(1)  # Simulating asynchronous I/O operation
        yield f"Data {i}\n"

# stream endpoint that receives json (question, session_id) and returns a streamed response
@app.post("/stream")
async def stream_response(data: dict):
    question = data["question"]
    session_id = data["session_id"]

    agent = get_agent(Agent.TEST, session_id, streaming=True)

    return StreamingResponse(run_agent(agent, question), media_type='text/plain')


uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))