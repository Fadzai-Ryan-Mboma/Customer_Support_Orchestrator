#!/usr/bin/env python3

import requests
import json
import time

def test_single_message():
    """Test a single password reset message"""
    
    url = "http://localhost:8000/api/v1/webhooks/whatsapp"
    
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "test_user_single",
                        "text": {
                            "body": "How do I reset my password?"
                        },
                        "type": "text"
                    }]
                }
            }]
        }]
    }
    
    print("🧪 Testing password reset classification...")
    response = requests.post(url, json=payload)
    print(f"📤 Response: {response.json()}")
    
    # Wait for processing
    time.sleep(3)
    
    # Check logs via docker
    import subprocess
    result = subprocess.run(
        ["docker", "compose", "-f", "docker-compose.poc.yml", "logs", "cassava-poc", "--tail", "50"],
        capture_output=True,
        text=True,
        cwd="/Users/fadzai/Documents/Cassava Code/Customer_Support_Orchestrator"
    )
    
    print("\n📋 Recent logs:")
    print(result.stdout[-2000:])  # Last 2000 characters

if __name__ == "__main__":
    test_single_message()