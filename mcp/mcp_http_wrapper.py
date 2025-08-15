from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio
import os
import sys
from dotenv import load_dotenv

# Garantir que o import funcione tanto rodando do diretório raiz quanto de mcp/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Carrega variáveis de ambiente e garante GRAPH_SERVICE_URL antes do import do MCP
load_dotenv()
if not os.environ.get("GRAPH_SERVICE_URL"):
    os.environ["GRAPH_SERVICE_URL"] = "http://localhost:10000"

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

# Endpoint alternativo que aceita JSON no corpo da requisição
from pydantic import BaseModel

class RunAgentRequest(BaseModel):
    thread_id: str
    user_input: str

@app.post("/run_agent_json")
async def run_agent_endpoint_json(payload: RunAgentRequest):
    try:
        response = await run_agent(payload.thread_id, payload.user_input)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
