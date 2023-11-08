from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents import get_agent, Agent
from agent_generator import *
import time
import asyncio
import os
import uvicorn

app = FastAPI()

origins = ["*"]

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