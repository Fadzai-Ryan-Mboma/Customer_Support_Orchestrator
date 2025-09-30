FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl redis-server && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Create directories
RUN mkdir -p /app/data /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1

# Start Redis and app
CMD redis-server --daemonize yes && uvicorn app.main:app --host 0.0.0.0 --port 8000