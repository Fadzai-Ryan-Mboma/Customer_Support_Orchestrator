"""
Telegram Channel Implementation for Cassava AI Support Orchestrator
"""

import os
import httpx
from typing import Dict, Any, Optional
from app.core.base_channel import BaseChannel, ChannelConnectionError

class TelegramChannel(BaseChannel):
    """
    Telegram Bot API channel implementation
    """
    
    def __init__(self):
        super().__init__("telegram")
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token:
            raise ChannelConnectionError("TELEGRAM_BOT_TOKEN not configured")
    
    async def send_message(self, to: str, content: str, **kwargs) -> bool:
        """
        Send message via Telegram Bot API
        
        Args:
            to: Chat ID
            content: Message text
            **kwargs: parse_mode, reply_to_message_id, etc.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/sendMessage",
                    json={
                        "chat_id": to,
                        "text": content,
                        "parse_mode": kwargs.get("parse_mode", "Markdown"),
                        "reply_to_message_id": kwargs.get("reply_to_message_id")
                    }
                )
                
                if response.status_code == 200:
                    self.logger.info(f"Message sent to Telegram chat {to}")
                    return True
                else:
                    self.logger.error(f"Telegram API error: {response.text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def parse_incoming_message(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Telegram webhook payload
        """
        try:
            if "message" not in raw_data:
                return None
            
            msg = raw_data["message"]
            
            return {
                "content": msg.get("text", ""),
                "sender": str(msg.get("from", {}).get("id", "")),
                "channel": "telegram",
                "message_id": str(msg.get("message_id", "")),
                "metadata": {
                    "chat_id": msg.get("chat", {}).get("id"),
                    "username": msg.get("from", {}).get("username"),
                    "first_name": msg.get("from", {}).get("first_name"),
                    "chat_type": msg.get("chat", {}).get("type")
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing Telegram message: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Telegram Bot API connection
        """
        try:
            import requests
            response = requests.get(f"{self.api_base}/getMe", timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                return {
                    "status": "connected",
                    "bot_info": bot_info.get("result", {})
                }
            else:
                return {
                    "status": "error",
                    "error": f"API returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def format_response(self, ai_response: str, **kwargs) -> str:
        """
        Format response for Telegram (supports Markdown)
        """
        # Add Cassava branding
        formatted = f"{ai_response}\n\n---\n*Cassava Network Support* 🤖"
        
        # Ensure message length is within Telegram limits (4096 characters)
        if len(formatted) > 4000:
            formatted = formatted[:3950] + "...\n\n---\n*Cassava Network Support* 🤖"
        
        return formatted
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get Telegram channel capabilities
        """
        return {
            "name": "telegram",
            "type": "TelegramChannel",
            "supports_media": True,
            "supports_formatting": True,
            "max_message_length": 4096,
            "supported_formats": ["Markdown", "HTML"],
            "features": ["inline_keyboards", "file_upload", "location_sharing"]
        }