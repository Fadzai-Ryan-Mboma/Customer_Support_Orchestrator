#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append('/Users/fadzai/Documents/Cassava Code/Customer_Support_Orchestrator')

from app.core.llm_gateway import LLMGateway
import json

async def test_classify():
    """Test the classify method directly"""
    gateway = LLMGateway()
    
    test_message = "How do I reset my password?"
    print(f"🧪 Testing message: '{test_message}'")
    
    result = await gateway.classify(test_message)
    
    print(f"🤖 Model used: {result.model_used}")
    print(f"📊 Success: {result.success}")
    print(f"📋 Raw content: {result.content}")
    
    try:
        classification = json.loads(result.content)
        print(f"🏷️ Parsed classification:")
        print(f"   • Priority: {classification['priority']}")
        print(f"   • Category: {classification['category']}")
        print(f"   • Sentiment: {classification['sentiment']}")
    except Exception as e:
        print(f"❌ Failed to parse: {e}")

if __name__ == "__main__":
    asyncio.run(test_classify())