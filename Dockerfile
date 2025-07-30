FROM python:3.13-slim

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

# Expor a porta pública (Graph Service)
EXPOSE 10000

# Rodar MCP em segundo plano + expor Graph Service publicamente
CMD python mcp/mcp_server.py & \
    uvicorn graph_service:app --host 0.0.0.0 --port 10000



