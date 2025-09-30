"""
Test webhook endpoint for demonstrating message processing
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
import json

from app.agents.master_orchestrator import MasterOrchestrator

router = APIRouter()
orchestrator = MasterOrchestrator()
logger = logging.getLogger(__name__)

@router.post("/test")
async def test_webhook(request: Request):
    """Test endpoint for processing customer messages"""
    try:
        data = await request.json()
        
        # Extract message content
        message_content = data.get("message", "")
        customer_id = data.get("customer_id", "test_customer")
        channel = data.get("channel", "test")
        
        if not message_content:
            raise HTTPException(status_code=400, detail="Message content is required")
        
        # Process message through orchestrator
        result = await orchestrator.process_message({
            "content": message_content,
            "channel": channel,
            "customer_id": customer_id,
            "message_id": f"test_{customer_id}"
        })
        
        logger.info(f"Processed test message: {result}")
        
        return {
            "status": "success",
            "processed_message": message_content,
            "customer_id": customer_id,
            "channel": channel,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))