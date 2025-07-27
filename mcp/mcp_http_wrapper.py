from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio
import os

# Importa seu MCP existente
from mcp.mcp_server import create_thread, run_agent

app = FastAPI(title="MCP HTTP Wrapper", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "MCP HTTP Wrapper is running"}

@app.post("/create_thread")
async def create_thread_endpoint():
    try:
        thread_id = await create_thread()
        return {"thread_id": thread_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_agent")
async def run_agent_endpoint(thread_id: str, user_input: str):
    try:
        response = await run_agent(thread_id, user_input)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
