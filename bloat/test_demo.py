#!/usr/bin/env python3
"""
Cassava Support Orchestrator - Demo Test Script
Tests the AI message processing functionality
"""

import requests
import json
import time
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🩺 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
    else:
        print("❌ Health check failed")
    print()

def test_ai_processing():
    """Test AI message processing with various scenarios"""
    print("🤖 Testing AI Message Processing...")
    
    test_messages = [
        {
            "message": "My payment failed and I can't access my account!",
            "customer_id": "customer_001",
            "channel": "whatsapp",
            "expected_category": "billing"
        },
        {
            "message": "The API keeps returning 500 errors when I try to upload files",
            "customer_id": "customer_002", 
            "channel": "email",
            "expected_category": "technical"
        },
        {
            "message": "Hi! I'd like to know more about your premium features",
            "customer_id": "customer_003",
            "channel": "telegram",
            "expected_category": "general"
        },
        {
            "message": "This is urgent! My entire system is down and I'm losing money!",
            "customer_id": "customer_004",
            "channel": "whatsapp",
            "expected_priority": "high"
        }
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"📝 Test {i}: {test['message'][:50]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/test/test",
                json=test,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Processing successful")
                print(f"   Customer: {result['customer_id']}")
                print(f"   Channel: {result['channel']}")
                
                if result['result']['success']:
                    classification = result['result']['classification']
                    print(f"   📊 Classification:")
                    print(f"      Priority: {classification.get('priority', 'N/A')}")
                    print(f"      Category: {classification.get('category', 'N/A')}")
                    print(f"      Sentiment: {classification.get('sentiment', 'N/A')}")
                    print(f"   🎫 Ticket ID: {result['result']['ticket_id']}")
                    print(f"   🤖 Model Used: {result['result']['model_used']}")
                    print(f"   💬 Response: {result['result']['response'][:100]}...")
                else:
                    print(f"   ⚠️  Fallback response: {result['result']['fallback_response']}")
            else:
                print(f"❌ Test failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - make sure the service is running")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
        
        print()
        time.sleep(1)  # Small delay between tests

def test_analytics():
    """Test analytics endpoint"""
    print("📊 Testing Analytics Dashboard...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard?tenant_id=demo_tenant&days=7")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics data retrieved successfully")
            print(f"   📈 Metrics for {data['period']}:")
            for key, value in data['metrics'].items():
                print(f"      {key.replace('_', ' ').title()}: {value}")
            print(f"   📱 Channel Distribution: {data['channel_distribution']}")
        else:
            print(f"❌ Analytics test failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
    
    print()

def test_conversations():
    """Test conversations endpoint"""
    print("💬 Testing Conversations API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/conversations/?tenant_id=demo_tenant")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversations data retrieved successfully")
            print(f"   📝 Total Conversations: {data['total']}")
            for conv in data['conversations']:
                print(f"      {conv['id']}: {conv['customer_name']} via {conv['channel']} ({conv['priority']})")
        else:
            print(f"❌ Conversations test failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Conversations test failed: {e}")
    
    print()

def test_webhook_simulation():
    """Simulate webhook calls"""
    print("🔗 Testing Webhook Simulation...")
    
    webhook_tests = [
        {
            "name": "WhatsApp Message",
            "url": f"{BASE_URL}/api/v1/webhooks/whatsapp",
            "data": {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "id": "msg_001",
                                "from": "1234567890",
                                "text": {"body": "I need help with my billing"}
                            }]
                        }
                    }]
                }]
            }
        },
        {
            "name": "Telegram Message", 
            "url": f"{BASE_URL}/api/v1/webhooks/telegram",
            "data": {
                "message": {
                    "text": "API is not working properly",
                    "from": {"id": "user123"},
                    "chat": {"id": "chat123"}
                }
            }
        }
    ]
    
    for test in webhook_tests:
        print(f"📱 Testing {test['name']}...")
        try:
            response = requests.post(
                test['url'],
                json=test['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Webhook processed successfully")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Webhook failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Webhook test failed: {e}")
        
        print()
        time.sleep(1)

def main():
    """Run all tests"""
    print("🚀 Cassava Support Orchestrator - Demo Test Suite")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    test_health()
    test_ai_processing() 
    test_analytics()
    test_conversations()
    test_webhook_simulation()
    
    print("=" * 60)
    print("🎉 Demo test suite completed!")
    print("\n📝 Next Steps:")
    print("   • Check the API documentation at http://localhost:8000/docs")
    print("   • View container logs: docker compose -f docker-compose.poc.yml logs -f")
    print("   • Configure real webhook URLs for WhatsApp/Telegram")
    print("   • Add your custom business logic and integrations")

if __name__ == "__main__":
    main()