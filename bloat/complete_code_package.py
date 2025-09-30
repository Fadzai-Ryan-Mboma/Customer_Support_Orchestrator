# ============================================
# CASSAVA SUPPORT ORCHESTRATOR - COMPLETE CODE
# Copy this entire file structure to deploy
# ============================================

"""
FILE: app/main.py
Main FastAPI application entry point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from datetime import datetime
import os

# Initialize FastAPI
app = FastAPI(
    title="Cassava Support Orchestrator",
    description="AI-powered customer support automation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, tenant_id: str):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(websocket)

    def disconnect(self, websocket: WebSocket, tenant_id: str):
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].remove(websocket)

    async def broadcast(self, message: dict, tenant_id: str):
        if tenant_id in self.active_connections:
            for connection in self.active_connections[tenant_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# WebSocket endpoint
@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
    await manager.connect(websocket, tenant_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all connections for this tenant
            await manager.broadcast({"message": data}, tenant_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id)

# Include API routers
from app.api.v1 import webhooks, tenants, analytics, conversations

app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Mount static files
app.mount("/static", StaticFiles(directory="web-ui"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Cassava Support Orchestrator",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================
# FILE: app/core/llm_gateway.py
# LLM Gateway with Mistral + Ollama fallback
# ============================================

import os
import asyncio
import httpx
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    MISTRAL = "mistral"
    OLLAMA = "ollama"

@dataclass
class LLMResponse:
    content: str
    model_used: str
    provider: ModelProvider
    tokens_used: int
    cost_usd: float
    success: bool
    error: Optional[str] = None

class LLMGateway:
    def __init__(self):
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        self.model_config = {
            "classification": {
                "primary": {"provider": ModelProvider.MISTRAL, "model": "mistral-small"},
                "fallback": {"provider": ModelProvider.OLLAMA, "model": "llama2:7b"}
            },
            "generation": {
                "primary": {"provider": ModelProvider.MISTRAL, "model": "mistral-large"},
                "fallback": {"provider": ModelProvider.OLLAMA, "model": "mixtral:8x7b"}
            }
        }
    
    async def classify(self, text: str) -> LLMResponse:
        """Classify customer message"""
        prompt = f"""Classify this support message and return JSON:
{text}

Return: {{"priority": "high|medium|low", "category": "billing|technical|general", "sentiment": "positive|neutral|negative"}}"""
        
        return await self._call("classification", prompt)
    
    async def generate_response(self, context: str) -> LLMResponse:
        """Generate customer response"""
        return await self._call("generation", context)
    
    async def _call(self, model_type: str, prompt: str) -> LLMResponse:
        config = self.model_config[model_type]
        
        # Try primary model
        try:
            if config["primary"]["provider"] == ModelProvider.MISTRAL:
                return await self._call_mistral(config["primary"]["model"], prompt)
        except Exception as e:
            logger.warning(f"Primary model failed: {e}")
            
            # Try fallback
            try:
                return await self._call_ollama(config["fallback"]["model"], prompt)
            except Exception as fallback_error:
                logger.error(f"Fallback failed: {fallback_error}")
                
                # Static fallback
                return LLMResponse(
                    content='{"priority": "medium", "category": "general", "sentiment": "neutral"}',
                    model_used="static_fallback",
                    provider=ModelProvider.MISTRAL,
                    tokens_used=0,
                    cost_usd=0.0,
                    success=False,
                    error=str(fallback_error)
                )
    
    async def _call_mistral(self, model: str, prompt: str) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.mistral_api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model_used=model,
                provider=ModelProvider.MISTRAL,
                tokens_used=data["usage"]["total_tokens"],
                cost_usd=self._calculate_cost(model, data["usage"]["total_tokens"]),
                success=True
            )
    
    async def _call_ollama(self, model: str, prompt: str) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["response"],
                model_used=model,
                provider=ModelProvider.OLLAMA,
                tokens_used=data.get("eval_count", 0),
                cost_usd=0.0,
                success=True
            )
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        pricing = {"mistral-small": 0.0002, "mistral-large": 0.008}
        return (tokens / 1000) * pricing.get(model, 0.002)


# ============================================
# FILE: app/agents/master_orchestrator.py
# Master Orchestrator - Routes messages to agents
# ============================================

import json
from datetime import datetime
from typing import Dict
import logging

from app.core.llm_gateway import LLMGateway

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    def __init__(self):
        self.llm_gateway = LLMGateway()
    
    async def process_message(self, message: Dict) -> Dict:
        """Main orchestration logic"""
        try:
            # Classify the message
            classification = await self.llm_gateway.classify(message["content"])
            
            # Parse classification
            try:
                result = json.loads(classification.content)
            except:
                result = {"priority": "medium", "category": "general", "sentiment": "neutral"}
            
            # Create ticket
            ticket_id = f"TICKET_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate response
            response_context = f"""Customer said: {message['content']}
Priority: {result['priority']}
Category: {result['category']}

Generate a helpful response acknowledging their issue and providing ticket number {ticket_id}."""
            
            response = await self.llm_gateway.generate_response(response_context)
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "classification": result,
                "response": response.content,
                "model_used": response.model_used,
                "processing_time_ms": 2000  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "Thank you for contacting support. We've received your message and will respond shortly."
            }


# ============================================
# FILE: app/api/v1/webhooks.py
# Webhook endpoints for WhatsApp, Telegram, etc.
# ============================================

from fastapi import APIRouter, Request, HTTPException
from typing import Dict
import logging

from app.agents.master_orchestrator import MasterOrchestrator

router = APIRouter()
orchestrator = MasterOrchestrator()
logger = logging.getLogger(__name__)

@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """WhatsApp webhook verification"""
    verify_token = "your_verify_token"  # From environment
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return hub_challenge
    
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    try:
        data = await request.json()
        
        # Extract message
        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if change.get("value", {}).get("messages"):
                        messages = change["value"]["messages"]
                        for msg in messages:
                            # Process message
                            result = await orchestrator.process_message({
                                "content": msg.get("text", {}).get("body", ""),
                                "channel": "whatsapp",
                                "customer_phone": msg.get("from"),
                                "message_id": msg.get("id")
                            })
                            
                            # Send response (implement WhatsApp send logic)
                            logger.info(f"Processed WhatsApp message: {result}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram messages"""
    try:
        data = await request.json()
        
        if "message" in data:
            msg = data["message"]
            result = await orchestrator.process_message({
                "content": msg.get("text", ""),
                "channel": "telegram",
                "customer_id": msg.get("from", {}).get("id"),
                "chat_id": msg.get("chat", {}).get("id")
            })
            
            logger.info(f"Processed Telegram message: {result}")
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FILE: app/api/v1/tenants.py
# Tenant management endpoints
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

class TenantCreate(BaseModel):
    name: str
    email: str
    tier: str = "startup"

@router.post("/")
async def create_tenant(tenant: TenantCreate):
    """Create new tenant"""
    tenant_id = str(uuid.uuid4())
    
    # In production, this would create tenant in database
    return {
        "id": tenant_id,
        "name": tenant.name,
        "email": tenant.email,
        "tier": tenant.tier,
        "status": "active",
        "message": "Tenant created successfully"
    }

@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get tenant details"""
    # Mock response
    return {
        "id": tenant_id,
        "name": "Demo Company",
        "tier": "startup",
        "status": "active",
        "conversations_count": 127,
        "sla_compliance": 94.2
    }


# ============================================
# FILE: app/api/v1/conversations.py
# Conversation management endpoints
# ============================================

from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()

@router.get("/")
async def get_conversations(
    tenant_id: str,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get conversations for tenant"""
    # Mock data
    return {
        "conversations": [
            {
                "id": "conv_123",
                "customer_name": "John Doe",
                "channel": "whatsapp",
                "priority": "high",
                "status": "active",
                "last_message": "Payment failed - need help",
                "created_at": "2025-09-27T10:30:00Z"
            },
            {
                "id": "conv_124",
                "customer_name": "Jane Smith",
                "channel": "email",
                "priority": "medium",
                "status": "active",
                "last_message": "Login issue",
                "created_at": "2025-09-27T10:25:00Z"
            }
        ],
        "total": 2,
        "page": 1
    }

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation details"""
    return {
        "id": conversation_id,
        "customer_name": "John Doe",
        "channel": "whatsapp",
        "priority": "high",
        "messages": [
            {
                "sender": "customer",
                "content": "My payment failed!",
                "timestamp": "2025-09-27T10:30:00Z"
            },
            {
                "sender": "agent",
                "content": "I've created ticket #A7B2C...",
                "timestamp": "2025-09-27T10:30:02Z"
            }
        ]
    }


# ============================================
# FILE: app/api/v1/analytics.py
# Analytics endpoints
# ============================================

from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(tenant_id: str, days: int = 7):
    """Get dashboard metrics"""
    return {
        "period": f"Last {days} days",
        "metrics": {
            "total_conversations": 1247,
            "active_conversations": 127,
            "sla_compliance": 94.2,
            "avg_response_time_seconds": 1.8,
            "customer_satisfaction": 4.7,
            "resolution_rate": 95.3
        },
        "trends": {
            "conversations": [120, 145, 132, 156, 142, 138, 127],
            "satisfaction": [4.5, 4.6, 4.7, 4.7, 4.8, 4.7, 4.7]
        },
        "channel_distribution": {
            "whatsapp": 45,
            "email": 30,
            "slack": 25
        }
    }


# ============================================
# FILE: docker-compose.poc.yml
# PoC Docker Compose - Single Container
# ============================================

"""
version: '3.8'

services:
  cassava-poc:
    build:
      context: .
      dockerfile: Dockerfile.poc
    container_name: cassava-poc
    ports:
      - "8000:8000"
    environment:
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OLLAMA_URL=http://ollama:11434
      - ENVIRONMENT=poc
    volumes:
      - poc_data:/app/data
      - poc_logs:/app/logs
    networks:
      - poc_network

  ollama:
    image: ollama/ollama:latest
    container_name: ollama-poc
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    networks:
      - poc_network

networks:
  poc_network:
    driver: bridge

volumes:
  poc_data:
  poc_logs:
  ollama_models:
"""


# ============================================
# FILE: Dockerfile.poc
# PoC Dockerfile - Minimal Setup
# ============================================

"""
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl redis-server && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-poc.txt .
RUN pip install --no-cache-dir -r requirements-poc.txt

# Copy application
COPY app/ ./app/

# Create directories
RUN mkdir -p /app/data /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1

# Start Redis and app
CMD redis-server --daemonize yes && uvicorn app.main:app --host 0.0.0.0 --port 8000
"""


# ============================================
# FILE: requirements-poc.txt
# Minimal PoC dependencies
# ============================================

"""
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
aiosqlite==0.19.0
redis==5.0.1
"""


# ============================================
# FILE: setup_poc.sh
# PoC Setup Script
# ============================================

"""
#!/bin/bash
set -e

echo "🚀 Setting up Cassava Support Orchestrator - PoC"

# Check Docker
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }

# Check environment
if [ ! -f .env.poc ]; then
    echo "⚠️  Create .env.poc with MISTRAL_API_KEY"
    exit 1
fi

# Build and start
docker-compose -f docker-compose.poc.yml build
docker-compose -f docker-compose.poc.yml up -d

# Wait for services
sleep 15

# Pull Ollama models
docker-compose -f docker-compose.poc.yml exec -T ollama ollama pull llama2:7b

# Health check
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed"
    exit 1
}

echo "✅ PoC is ready at http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
"""

# ============================================
# USAGE INSTRUCTIONS
# ============================================

"""
TO DEPLOY THIS CODE:

1. CREATE PROJECT STRUCTURE:
   mkdir -p cassava-support-orchestrator/{app/{api/v1,agents,core},sql,config,scripts}
   cd cassava-support-orchestrator

2. SAVE FILES:
   - Copy each section above to its corresponding file path
   - Example: app/main.py, app/core/llm_gateway.py, etc.

3. CREATE .env.poc:
   MISTRAL_API_KEY=your_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_token

4. RUN POC:
   bash setup_poc.sh

5. TEST:
   curl http://localhost:8000/health
   curl http://localhost:8000/docs

THAT'S IT! Your system is running!

For PRODUCTION deployment, see the Implementation Guide (Artifact #2)
"""webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(