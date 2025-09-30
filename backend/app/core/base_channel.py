"""
Base Channel Interface for Cassava AI Support Orchestrator
Provides unified interface for all communication channels
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseChannel(ABC):
    """
    Abstract base class for all communication channels
    """
    
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.logger = logging.getLogger(f"{__name__}.{channel_name}")
    
    @abstractmethod
    async def send_message(self, to: str, content: str, **kwargs) -> bool:
        """
        Send a message through this channel
        
        Args:
            to: Recipient identifier (phone, email, user_id, etc.)
            content: Message content
            **kwargs: Channel-specific parameters
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def parse_incoming_message(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook data into standardized format
        
        Args:
            raw_data: Raw webhook payload
            
        Returns:
            Dict with standardized fields:
            {
                "content": str,
                "sender": str,
                "channel": str,
                "message_id": str,
                "metadata": dict
            }
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test channel connectivity
        
        Returns:
            Dict with connection status and details
        """
        pass
    
    def format_response(self, ai_response: str, **kwargs) -> str:
        """
        Format AI response for this channel (can be overridden)
        
        Args:
            ai_response: Raw AI response
            **kwargs: Channel-specific formatting options
            
        Returns:
            Formatted response string
        """
        return ai_response
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get channel information and capabilities
        """
        return {
            "name": self.channel_name,
            "type": self.__class__.__name__,
            "supports_media": False,
            "supports_formatting": False,
            "max_message_length": 1000
        }

class MessageProcessingError(Exception):
    """Custom exception for message processing errors"""
    pass

class ChannelConnectionError(Exception):
    """Custom exception for channel connection errors"""
    pass