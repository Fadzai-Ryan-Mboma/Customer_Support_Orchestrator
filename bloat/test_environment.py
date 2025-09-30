#!/usr/bin/env python3
"""
Environment and API Testing Script
Tests if environment variables and APIs are properly configured
"""

import os
import requests
import asyncio
import httpx
from datetime import datetime

def test_environment_variables():
    """Test if environment variables are properly loaded"""
    print("🔍 Testing Environment Variables...")
    print("-" * 40)
    
    # Check Mistral API Key
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key and mistral_key != "your_mistral_api_key_here":
        print(f"✅ MISTRAL_API_KEY: Set (length: {len(mistral_key)})")
        # Test Mistral API connection
        test_mistral_connection(mistral_key)
    else:
        print("❌ MISTRAL_API_KEY: Not set or using placeholder")
    
    # Check Telegram Bot Token
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if telegram_token and telegram_token != "your_telegram_bot_token_here":
        print(f"✅ TELEGRAM_BOT_TOKEN: Set (length: {len(telegram_token)})")
    else:
        print("❌ TELEGRAM_BOT_TOKEN: Not set or using placeholder")
    
    # Check other environment variables
    env_vars = ["ENVIRONMENT", "DEBUG", "OLLAMA_URL"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print()

def test_mistral_connection(api_key):
    """Test Mistral API connection"""
    print("🤖 Testing Mistral API Connection...")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-tiny",
            "messages": [{"role": "user", "content": "Hello, this is a test message."}],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ Mistral API: Connected successfully")
            print(f"   Test response: {content[:100]}...")
            return True
        else:
            print(f"❌ Mistral API: Failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Mistral API: Connection failed - {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("🦙 Testing Ollama Connection...")
    
    try:
        # Test Ollama health
        response = requests.get("http://localhost:11434/", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama: Server is running")
            
            # Test model availability
            try:
                models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if models_response.status_code == 200:
                    models = models_response.json()
                    if models.get("models"):
                        print(f"✅ Ollama: {len(models['models'])} models available")
                        for model in models["models"]:
                            print(f"   - {model['name']}")
                    else:
                        print("⚠️  Ollama: No models found - run 'ollama pull llama2:7b'")
                else:
                    print("⚠️  Ollama: Cannot list models")
            except:
                print("⚠️  Ollama: Cannot check models")
        else:
            print(f"❌ Ollama: Server returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama: Cannot connect - make sure Ollama container is running")
    except Exception as e:
        print(f"❌ Ollama: Error - {e}")
    
    print()

def test_service_endpoints():
    """Test service endpoints"""
    print("🌐 Testing Service Endpoints...")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    endpoints = [
        {"url": f"{base_url}/health", "name": "Health Check"},
        {"url": f"{base_url}/docs", "name": "API Documentation"},
        {"url": f"{base_url}/api/v1/analytics/dashboard?tenant_id=test", "name": "Analytics"},
        {"url": f"{base_url}/api/v1/conversations/?tenant_id=test", "name": "Conversations"}
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint["url"], timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint['name']}: Working")
            else:
                print(f"❌ {endpoint['name']}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint['name']}: Error - {e}")
    
    print()

def test_ai_processing():
    """Test AI processing with a simple message"""
    print("🧠 Testing AI Message Processing...")
    print("-" * 40)
    
    test_message = {
        "message": "Hello, I need help with my account",
        "customer_id": "env_test_customer",
        "channel": "test"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/test/test",
            json=test_message,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Processing: Working")
            
            if result["result"]["success"]:
                print(f"   Model Used: {result['result']['model_used']}")
                print(f"   Ticket ID: {result['result']['ticket_id']}")
                
                classification = result["result"]["classification"]
                print(f"   Classification: {classification}")
            else:
                print(f"   Fallback Response: {result['result']['fallback_response']}")
                
        else:
            print(f"❌ AI Processing: Failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ AI Processing: Error - {e}")
    
    print()

def main():
    """Run all tests"""
    print("🔧 Cassava Support Orchestrator - Environment Test")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load environment variables from .env.poc if it exists
    env_file = ".env.poc"
    if os.path.exists(env_file):
        print(f"📄 Loading environment from {env_file}...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print()
    
    # Run tests
    test_environment_variables()
    test_ollama_connection()
    test_service_endpoints()
    test_ai_processing()
    
    print("=" * 60)
    print("🎯 Environment test completed!")
    print()
    print("📋 Summary:")
    print("   • If Mistral API is working, your AI responses will be intelligent")
    print("   • If only Ollama is working, responses will use local models") 
    print("   • If neither works, you'll get static fallback responses")
    print()
    print("🛠️  Next Steps:")
    print("   • Ensure your MISTRAL_API_KEY is set correctly in .env.poc")
    print("   • Check that Docker containers are running properly")
    print("   • View logs with: docker compose -f docker-compose.poc.yml logs -f")

if __name__ == "__main__":
    main()