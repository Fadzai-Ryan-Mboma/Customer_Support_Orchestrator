"""
Customer Support Orchestrator - Main Application
FastAPI application with WebSocket support and multi-channel integration
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

# Add the app directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables explicitly
from dotenv import load_dotenv

# Try to load environment file
env_file = Path(".env")  # Updated to match new location
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print("⚠️ No .env file found, using system environment")

# Import routers
from api.v1 import (
    webhooks,
    conversations,
    analytics,
    tenants,
    test,
    health
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
ALLOWED_METHODS = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
ALLOWED_HEADERS = os.getenv("ALLOWED_HEADERS", "*").split(",")

print(f"🚀 Starting Customer Support Orchestrator")
print(f"Environment: {ENVIRONMENT}")
print(f"Debug Mode: {DEBUG}")
print(f"Host: {APP_HOST}:{APP_PORT}")
print(f"Allowed Origins: {ALLOWED_ORIGINS}")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🚀 Customer Support Orchestrator starting up...")
    
    # Check environment variables
    required_vars = ["MISTRAL_API_KEY", "TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here"]
    
    if missing_vars:
        print(f"⚠️ Warning: Missing environment variables: {missing_vars}")
        print("🔧 The system will use fallback responses for AI processing")
    else:
        print("✅ All required environment variables are configured")
    
    # Initialize channel manager and services
    try:
        from core.channel_manager import ChannelManager
        channel_manager = ChannelManager()
        
        # Test all channels
        channel_results = await channel_manager.test_all_channels()
        active_channels = [name for name, result in channel_results.items() if result.get("status") == "connected"]
        
        if active_channels:
            print(f"✅ Active channels: {', '.join(active_channels)}")
        else:
            print("⚠️ No channels are currently active")
        
        # Start email polling if email channel is active
        if "email" in active_channels:
            email_channel = channel_manager.get_channel("email")
            if email_channel and hasattr(email_channel, 'email_service'):
                import asyncio
                email_task = asyncio.create_task(email_channel.email_service.start_email_polling())
                print("📧 Email polling service started")
            
    except Exception as e:
        print(f"⚠️ Channel manager initialization failed: {e}")
    
    yield
    
    print("🛑 Customer Support Orchestrator shutting down...")
    # Cancel email polling task if it exists
    try:
        if 'email_task' in locals():
            email_task.cancel()
            print("📧 Email polling service stopped")
    except:
        pass

# Create FastAPI application
app = FastAPI(
    title="Customer Support Orchestrator",
    description="AI-powered multi-channel customer support system",
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

# Mount static files (web UI)
static_path = Path("/app/static")  # Frontend files are mounted here in Docker
local_frontend = Path("../frontend")  # Local development path
local_img = Path("../img")  # Image assets (local)
docker_img = Path("/app/img")  # Image assets (Docker)

if static_path.exists():
    app.mount("/ui", StaticFiles(directory="/app/static", html=True), name="static")
    print("✅ Mounted web UI at /ui from Docker volume")
elif local_frontend.exists():
    app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="static")
    print("✅ Mounted web UI at /ui from local frontend directory")
else:
    print("⚠️ Frontend directory not found. Web UI will not be available.")
    local_static_path = Path("../frontend")
    if local_static_path.exists():
        app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="static")
        print("✅ Mounted web UI at /ui (local)")
    else:
        print("⚠️ Frontend directory not found")

# Mount image assets
if docker_img.exists():
    app.mount("/img", StaticFiles(directory="/app/img"), name="images")
    print("✅ Mounted images at /img from Docker volume")
elif local_img.exists():
    app.mount("/img", StaticFiles(directory="../img"), name="images")
    print("✅ Mounted images at /img from local directory")
else:
    print("⚠️ Image directory not found")

# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(test.router, prefix="/api/v1/test", tags=["Testing"])

# Root endpoint
@app.get("/")
async def root():
    """Redirect to the web UI dashboard"""
    return RedirectResponse(url="/ui/")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo received message for testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Broadcast function for other modules
async def broadcast_update(message: dict):
    """Function to broadcast updates to all connected WebSocket clients"""
    await manager.broadcast(message)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)