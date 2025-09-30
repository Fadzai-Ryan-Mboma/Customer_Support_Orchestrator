"""
Master Orchestrator - Routes messages to agents
"""

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