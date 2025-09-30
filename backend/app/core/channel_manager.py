"""
Channel Manager for Cassava AI Support Orchestrator
Manages all communication channels and provides unified interface
"""

import logging
from typing import Dict, Any, Optional, List
from app.core.base_channel import BaseChannel, ChannelConnectionError
from app.core.telegram_channel import TelegramChannel
from app.core.email_channel import EmailChannel
from app.agents.master_orchestrator import MasterOrchestrator

logger = logging.getLogger(__name__)

class ChannelManager:
    """
    Manages all communication channels and provides unified message processing
    """
    
    def __init__(self):
        self.channels: Dict[str, BaseChannel] = {}
        self.orchestrator = MasterOrchestrator()
        self._initialize_channels()
    
    def _initialize_channels(self):
        """
        Initialize all available channels
        """
        # Initialize Telegram channel
        try:
            telegram = TelegramChannel()
            self.channels["telegram"] = telegram
            logger.info("✅ Telegram channel initialized")
        except ChannelConnectionError as e:
            logger.warning(f"⚠️ Telegram channel not available: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram channel: {e}")
        
        # Initialize Email channel
        try:
            email = EmailChannel()
            self.channels["email"] = email
            logger.info("✅ Email channel initialized")
        except ChannelConnectionError as e:
            logger.warning(f"⚠️ Email channel not available: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Email channel: {e}")
        
        logger.info(f"📡 Channel Manager initialized with {len(self.channels)} channels: {list(self.channels.keys())}")
    
    async def process_message(self, channel_name: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message through appropriate channel
        
        Args:
            channel_name: Name of the channel (telegram, email, etc.)
            raw_data: Raw webhook/message data
            
        Returns:
            Processing result with response
        """
        try:
            # Get channel
            channel = self.channels.get(channel_name)
            if not channel:
                raise ValueError(f"Channel '{channel_name}' not available")
            
            # Parse message
            parsed_message = channel.parse_incoming_message(raw_data)
            if not parsed_message:
                raise ValueError("Failed to parse incoming message")
            
            # Process through orchestrator
            result = await self.orchestrator.process_message(parsed_message)
            
            # Send response if we have one
            if result and result.get('response'):
                # Format response for channel
                formatted_response = channel.format_response(result['response'])
                
                # Get channel-specific send parameters
                send_params = self._get_channel_send_params(channel_name, parsed_message, raw_data)
                
                # For Telegram, use chat_id instead of sender if available
                recipient = send_params.pop("to", parsed_message['sender'])
                
                # Send response
                success = await channel.send_message(
                    to=recipient,
                    content=formatted_response,
                    **send_params
                )
                
                result['sent'] = success
                if success:
                    logger.info(f"✅ Response sent via {channel_name} to {recipient}")
                else:
                    logger.error(f"❌ Failed to send response via {channel_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {channel_name} message: {e}")
            return {
                "error": str(e),
                "channel": channel_name,
                "processed": False
            }
    
    def _get_channel_send_params(self, channel_name: str, parsed_message: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get channel-specific parameters for sending response
        """
        params = {}
        
        if channel_name == "telegram":
            # For Telegram, we need chat_id and might want to reply to specific message
            params["to"] = parsed_message["metadata"].get("chat_id", parsed_message["sender"])
            if parsed_message.get("message_id"):
                params["reply_to_message_id"] = int(parsed_message["message_id"])
        
        elif channel_name == "email":
            # For email, we need proper subject and threading
            subject = parsed_message["metadata"].get("subject", "")
            if subject and not subject.startswith("Re:"):
                params["subject"] = f"Re: {subject}"
            else:
                params["subject"] = subject or "Response from Cassava Support"
            
            if parsed_message.get("message_id"):
                params["in_reply_to"] = parsed_message["message_id"]
        
        return params
    
    def get_channel_status(self) -> Dict[str, Any]:
        """
        Get status of all channels
        """
        status = {
            "total_channels": len(self.channels),
            "active_channels": [],
            "channel_details": {}
        }
        
        for name, channel in self.channels.items():
            try:
                connection_test = channel.test_connection()
                channel_info = channel.get_channel_info()
                
                is_active = connection_test.get("status") == "connected"
                if is_active:
                    status["active_channels"].append(name)
                
                status["channel_details"][name] = {
                    "active": is_active,
                    "connection": connection_test,
                    "info": channel_info
                }
                
            except Exception as e:
                status["channel_details"][name] = {
                    "active": False,
                    "error": str(e)
                }
        
        return status
    
    def get_available_channels(self) -> List[str]:
        """
        Get list of available channel names
        """
        return list(self.channels.keys())
    
    def get_channel(self, channel_name: str) -> Optional[BaseChannel]:
        """
        Get specific channel instance
        """
        return self.channels.get(channel_name)
    
    async def test_all_channels(self) -> Dict[str, Any]:
        """
        Test all channels and return results
        """
        results = {}
        
        for name, channel in self.channels.items():
            try:
                results[name] = channel.test_connection()
                logger.info(f"Tested {name} channel: {results[name]['status']}")
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
                logger.error(f"Error testing {name} channel: {e}")
        
        return results
    
    async def send_test_message(self, channel_name: str, to: str, message: str = None) -> bool:
        """
        Send a test message through specific channel
        """
        try:
            channel = self.channels.get(channel_name)
            if not channel:
                logger.error(f"Channel '{channel_name}' not available")
                return False
            
            test_message = message or f"Test message from Cassava AI Support System via {channel_name.title()}"
            
            return await channel.send_message(to, test_message)
            
        except Exception as e:
            logger.error(f"Error sending test message via {channel_name}: {e}")
            return False