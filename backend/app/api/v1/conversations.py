"""
Conversation management endpoints
"""

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