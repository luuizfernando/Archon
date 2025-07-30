FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências primeiro (cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expor porta principal
EXPOSE 10000

# Executar MCP como background + Graph Service como principal
CMD python -m mcp.mcp_server & \
    uvicorn graph_service:app --host 0.0.0.0 --port 10000
