#!/usr/bin/env python3

import requests
import json
import time

def test_password_classification():
    """Test password reset classification specifically"""
    
    url = "http://localhost:8000/api/v1/webhooks/whatsapp"
    
    # Test message
    test_message = "How do I reset my password?"
    
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "debug_user",
                        "text": {
                            "body": test_message
                        },
                        "type": "text"
                    }]
                }
            }]
        }]
    }
    
    print(f"🧪 Testing message: '{test_message}'")
    print(f"📝 Lowercase version: '{test_message.lower()}'")
    print(f"🔍 Contains 'reset': {'reset' in test_message.lower()}")
    print(f"🔍 Contains 'password': {'password' in test_message.lower()}")
    
    # Send message
    response = requests.post(url, json=payload)
    print(f"📤 Response: {response.json()}")
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Let's manually check the keywords
    prompt_lower = test_message.lower()
    technical_keywords = ["login", "password", "app", "website", "technical", "bug", "error", "crash", "slow", "reset", "access", "account", "reset password"]
    
    print(f"\n🔧 Manual keyword checking:")
    for keyword in technical_keywords:
        if keyword in prompt_lower:
            print(f"   ✅ Found: '{keyword}'")
    
    # Check special condition
    if "reset" in prompt_lower and "password" in prompt_lower:
        print(f"   🎯 Special condition matched: reset + password")
    else:
        print(f"   ❌ Special condition not matched")

if __name__ == "__main__":
    test_password_classification()