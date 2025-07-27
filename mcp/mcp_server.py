from mcp.server.fastmcp import FastMCP
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List
import threading
import requests
import asyncio
import uuid
import sys
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server with ERROR logging level
mcp = FastMCP("archon", log_level="ERROR")

# Store active threads
active_threads: Dict[str, List[str]] = {}

# FastAPI service URL
GRAPH_SERVICE_URL = os.getenv("GRAPH_SERVICE_URL", "http://localhost:8100")

def write_to_log(message: str):
    """Write a message to the logs.txt file in the workbench directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    workbench_dir = os.path.join(parent_dir, "workbench")
    log_path = os.path.join(workbench_dir, "logs.txt")
    os.makedirs(workbench_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

@mcp.tool()
async def create_thread() -> str:
    thread_id = str(uuid.uuid4())
    active_threads[thread_id] = []
    write_to_log(f"Created new thread: {thread_id}")
    return thread_id

def _make_request(thread_id: str, user_input: str, config: dict) -> str:
    try:
        response = requests.post(
            f"{GRAPH_SERVICE_URL}/invoke",
            json={
                "message": user_input,
                "thread_id": thread_id,
                "is_first_message": not active_threads[thread_id],
                "config": config
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        write_to_log(f"Request timed out for thread {thread_id}")
        raise TimeoutError("Request to graph service timed out.")
    except requests.exceptions.RequestException as e:
        write_to_log(f"Request failed for thread {thread_id}: {str(e)}")
        raise

@mcp.tool()
async def run_agent(thread_id: str, user_input: str) -> str:
    if thread_id not in active_threads:
        write_to_log(f"Error: Thread not found - {thread_id}")
        raise ValueError("Thread not found")

    write_to_log(f"Processing message for thread {thread_id}: {user_input}")

    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await asyncio.to_thread(_make_request, thread_id, user_input, config)
        active_threads[thread_id].append(user_input)
        return result['response']
    except Exception as e:
        raise

if __name__ == "__main__":
    print("Servidor MCP iniciado!")
    write_to_log("Starting MCP server")
    mcp.run(transport="http")


