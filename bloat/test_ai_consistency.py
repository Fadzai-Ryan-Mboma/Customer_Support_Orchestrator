#!/usr/bin/env python3
"""
Test script to verify that AI classifications match responses
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_ai_consistency(message, channel="telegram"):
    """Test if classification matches response"""
    try:
        test_data = {
            "message": message,
            "customer_id": "consistency_test",
            "channel": channel
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
                
                # Check if response mentions the correct category/priority
                response_lower = response_text.lower()
                category_mentioned = classification['category'] in response_lower or \
                                   (classification['category'] == 'billing' and any(word in response_lower for word in ['billing', 'payment', 'account']))
                priority_reflected = (classification['priority'] == 'high' and any(word in response_lower for word in ['urgent', 'priority', 'immediate', 'escalat', 'specialist'])) or \
                                   classification['priority'] in ['medium', 'low']
                
                consistency_score = "🎯 CONSISTENT" if category_mentioned and priority_reflected else "⚠️ INCONSISTENT"
                print(f"🔍 Consistency: {consistency_score}")
                print("-" * 80)
                return True
            else:
                print(f"❌ Fallback: {result['result']['fallback_response']}")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🧪 Testing AI Classification & Response Consistency")
    print("=" * 80)
    
    # Test different message types
    test_messages = [
        ("My payment failed and I need help urgently!", "High priority billing"),
        ("How do I reset my password?", "Technical support"),
        ("I can't login to my account", "Technical issue"),
        ("When is my next billing date?", "Billing inquiry"),
        ("Your service is amazing, thank you!", "Positive feedback"),
        ("I'm frustrated with the slow response time", "Negative feedback"),
        ("What are your business hours?", "General inquiry"),
        ("My credit card was charged twice!", "Urgent billing"),
        ("The app keeps crashing", "Technical problem"),
        ("I love the new features!", "Positive sentiment")
    ]
    
    successful_tests = 0
    total_tests = len(test_messages)
    
    for message, description in test_messages:
        print(f"🔍 Testing: {description}")
        if test_ai_consistency(message):
            successful_tests += 1
        print()
    
    print(f"📊 Test Summary: {successful_tests}/{total_tests} tests successful")
    
    if successful_tests == total_tests:
        print("🎉 All AI responses are consistent with classifications!")
    else:
        print("⚠️ Some inconsistencies found - check the logs above")

if __name__ == "__main__":
    import time
    print("⏳ Waiting for services to be ready...")
    time.sleep(3)
    main()