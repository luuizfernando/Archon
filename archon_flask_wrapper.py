from flask import Flask, request, jsonify
import subprocess
import json
import sys
import os

# Caminho para o script do MCP Archon
ARCHON_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mcp', 'mcp_server.py'))

app = Flask(__name__)

def call_archon_tool(tool, args=None):
    """
    Chama o MCP Archon como subprocesso, passando o nome da tool e argumentos.
    """
    cmd = [sys.executable, ARCHON_SCRIPT, tool]
    if args:
        cmd.append(json.dumps(args))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}, 500
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"error": "Resposta inválida do Archon", "raw": result.stdout}, 500

@app.route("/create_thread", methods=["POST"])
def create_thread():
    response = call_archon_tool("create_thread")
    return jsonify(response)

@app.route("/run_agent", methods=["POST"])
def run_agent():
    data = request.get_json()
    response = call_archon_tool("run_agent", data)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502, debug=True) 