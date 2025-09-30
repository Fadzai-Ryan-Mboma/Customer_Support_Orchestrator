"""
Email Channel Implementation for Cassava AI Support Orchestrator
"""

import os
import re
from typing import Dict, Any, Optional
from app.core.base_channel import BaseChannel, ChannelConnectionError
from app.core.email_service import EmailService

class EmailChannel(BaseChannel):
    """
    Email channel implementation using EmailService
    """
    
    def __init__(self):
        super().__init__("email")
        self.email_service = EmailService()
        
        # Verify email configuration
        if not all([
            os.getenv('EMAIL_USERNAME'),
            os.getenv('EMAIL_PASSWORD'),
            os.getenv('EMAIL_SMTP_HOST')
        ]):
            raise ChannelConnectionError("Email configuration incomplete")
    
    async def send_message(self, to: str, content: str, **kwargs) -> bool:
        """
        Send email message
        
        Args:
            to: Email address
            content: Message content
            **kwargs: subject, in_reply_to, etc.
        """
        try:
            subject = kwargs.get("subject", "Response from Cassava Support")
            in_reply_to = kwargs.get("in_reply_to")
            
            return await self.email_service.send_email(
                to_email=to,
                subject=subject,
                content=content,
                in_reply_to=in_reply_to
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def parse_incoming_message(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse email webhook or polling data
        """
        try:
            # Handle both webhook and polling formats
            if "from" in raw_data and "content" in raw_data:
                # Direct email format (from polling)
                return {
                    "content": raw_data.get("content", ""),
                    "sender": self._extract_email_address(raw_data.get("from", "")),
                    "channel": "email",
                    "message_id": raw_data.get("message_id", ""),
                    "metadata": {
                        "subject": raw_data.get("subject", ""),
                        "received_at": raw_data.get("received_at"),
                        "full_from": raw_data.get("from", "")
                    }
                }
            else:
                # Webhook format (varies by provider)
                return {
                    "content": raw_data.get("text", raw_data.get("body", "")),
                    "sender": self._extract_email_address(raw_data.get("from", "")),
                    "channel": "email",
                    "message_id": raw_data.get("message_id", raw_data.get("id", "")),
                    "metadata": {
                        "subject": raw_data.get("subject", ""),
                        "provider": raw_data.get("provider", "unknown")
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error parsing email message: {e}")
            return None
    
    def _extract_email_address(self, from_field: str) -> str:
        """
        Extract email address from 'Name <email@domain.com>' format
        """
        if not from_field:
            return ""
        
        # Use regex to extract email from various formats
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, from_field)
        
        return matches[0] if matches else from_field.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test email service connection
        """
        try:
            results = self.email_service.test_connection()
            
            if results["smtp"] and results["imap"]:
                return {
                    "status": "connected",
                    "smtp": results["smtp"],
                    "imap": results["imap"]
                }
            else:
                return {
                    "status": "error",
                    "errors": results["errors"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def format_response(self, ai_response: str, **kwargs) -> str:
        """
        Format response for email
        """
        # Add professional email formatting
        formatted = f"""Dear Customer,

{ai_response}

Thank you for contacting Cassava Network Support. We're here to help you with any questions or concerns you may have.

If you need immediate assistance, please don't hesitate to reach out to our support team directly.

Best regards,
Cassava Network Support Team

---
This is an automated response from Cassava AI Support System.
For urgent matters, please contact our support team directly.
"""
        
        return formatted
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Get email channel capabilities
        """
        return {
            "name": "email",
            "type": "EmailChannel",
            "supports_media": True,
            "supports_formatting": True,
            "max_message_length": 50000,  # Most email providers support large messages
            "supported_formats": ["plain_text", "html"],
            "features": ["threading", "attachments", "html_formatting", "auto_polling"]
        }