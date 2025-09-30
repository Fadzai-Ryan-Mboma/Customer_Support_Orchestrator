#!/usr/bin/env python3

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_single_password_reset():
    """Test just the password reset message"""
    message = "How do I reset my password?"
    
    test_data = {
        "message": message,
        "customer_id": "consistency_test",
        "channel": "telegram"
    }
    
    response = requests.post(f"{API_BASE}/test/test", 
                           json=test_data,
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        result = response.json()
        if result["result"]["success"]:
            classification = result["result"]["classification"]
            response_text = result["result"]["response"]
            model_used = result["result"]["model_used"]
            
            print(f"✅ Message: '{message}'")
            print(f"🤖 Model: {model_used}")
            print(f"📊 Classification:")
            print(f"   • Priority: {classification['priority']}")
            print(f"   • Category: {classification['category']}")
            print(f"   • Sentiment: {classification['sentiment']}")
            print(f"💬 Response: {response_text}")
            
            return classification
        else:
            print(f"❌ Processing failed")
            return None
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    test_single_password_reset()