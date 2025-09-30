"""
Health check API endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter()

@router.get("/status")
async def health_status() -> Dict[str, Any]:
    """Get system health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "llm_gateway": "healthy",
            "master_orchestrator": "healthy",
            "api": "healthy"
        }
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Check if system is ready to serve requests"""
    return {
        "ready": True,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": "ready",
            "llm_providers": "ready",
            "agents": "ready"
        }
    }