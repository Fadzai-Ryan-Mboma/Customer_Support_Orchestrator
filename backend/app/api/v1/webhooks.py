"""
Webhook endpoints for multi-channel communication
Using unified channel manager for consistent message processing
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict
import logging

from app.core.channel_manager import ChannelManager

router = APIRouter()
channel_manager = ChannelManager()
logger = logging.getLogger(__name__)

# POC Configuration: Telegram and Email webhooks only

@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram messages via unified channel manager"""
    try:
        data = await request.json()
        result = await channel_manager.process_message("telegram", data)
        
        logger.info(f"Processed Telegram message: {result}")
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email")
async def email_webhook(request: Request):
    """Handle incoming email messages via unified channel manager"""
    try:
        data = await request.json()
        result = await channel_manager.process_message("email", data)
        
        logger.info(f"Processed email webhook: {result}")
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Email webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels/status")
async def get_channels_status():
    """Get status of all communication channels"""
    try:
        status = channel_manager.get_channel_status()
        return status
    except Exception as e:
        logger.error(f"Error getting channel status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels/test")
async def test_all_channels():
    """Test all communication channels"""
    try:
        results = await channel_manager.test_all_channels()
        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error testing channels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels/{channel_name}/send")
async def send_test_message(channel_name: str, request: Request):
    """Send test message through specific channel"""
    try:
        data = await request.json()
        
        result = await channel_manager.send_test_message(
            channel_name=channel_name,
            to=data.get("to"),
            message=data.get("message")
        )
        
        return {
            "status": "sent" if result else "failed",
            "channel": channel_name,
            "message": "Test message sent successfully" if result else "Failed to send test message"
        }
        
    except Exception as e:
        logger.error(f"Send test message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))