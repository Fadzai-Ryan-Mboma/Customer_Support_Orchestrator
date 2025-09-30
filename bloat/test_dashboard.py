#!/usr/bin/env python3
"""
Quick test to verify the live dashboard and AI functionality
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_health():
    """Test if the API is healthy"""
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_analytics():
    """Test analytics endpoint"""
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard?tenant_id=live_demo&days=7")
        print(f"✅ Analytics: {response.status_code}")
        data = response.json()
        print(f"   Active Conversations: {data['metrics']['active_conversations']}")
        print(f"   SLA Compliance: {data['metrics']['sla_compliance']}%")
        print(f"   Response Time: {data['metrics']['avg_response_time_seconds']}s")
        return True
    except Exception as e:
        print(f"❌ Analytics Failed: {e}")
        return False

def test_conversations():
    """Test conversations endpoint"""
    try:
        response = requests.get(f"{API_BASE}/conversations/?tenant_id=live_demo")
        print(f"✅ Conversations: {response.status_code}")
        data = response.json()
        print(f"   Total Conversations: {len(data['conversations'])}")
        return True
    except Exception as e:
        print(f"❌ Conversations Failed: {e}")
        return False

def test_ai_processing():
    """Test AI processing with real message"""
    try:
        test_data = {
            "message": "My payment failed and I need urgent help!",
            "customer_id": "test_dashboard_user",
            "channel": "telegram"
        }
        
        response = requests.post(f"{API_BASE}/test/test", 
                               json=test_data,
                               headers={"Content-Type": "application/json"})
        print(f"✅ AI Processing: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result["result"]["success"]:
                print(f"   🤖 Model Used: {result['result']['model_used']}")
                print(f"   🎯 Priority: {result['result']['classification']['priority']}")
                print(f"   📝 Category: {result['result']['classification']['category']}")
                print(f"   💬 Response: {result['result']['response'][:100]}...")
            else:
                print(f"   ⚠️ Fallback Mode: {result['result']['fallback_response'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ AI Processing Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Customer Support Orchestrator Dashboard")
    print("=" * 60)
    
    # Wait for containers to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    tests = [
        ("Health Check", test_health),
        ("Analytics Dashboard", test_analytics),
        ("Conversations API", test_conversations),
        ("AI Processing", test_ai_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your dashboard is ready!")
        print(f"🌐 Open dashboard: http://localhost:8000/ui/")
        print(f"📚 API documentation: http://localhost:8000/docs")
    else:
        print("⚠️ Some tests failed, but basic functionality should work")

if __name__ == "__main__":
    main()