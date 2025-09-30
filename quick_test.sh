#!/bin/bash

# Quick AI & Channel Test Script
echo "🔬 QUICK TEST SCRIPT"
echo "==================="

# Test Ollama directly
echo "Testing Ollama directly:"
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "prompt": "What is Cassava Network?",
    "stream": false
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('✅ Ollama Response:', data.get('response', 'No response')[:100] + '...')
except:
    print('❌ Ollama failed')
"

echo ""

# Test Mistral API directly (to see raw error)
echo "Testing Mistral API directly:"
API_KEY=$(docker exec cassava-ai-poc printenv MISTRAL_API_KEY)
curl -X POST https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'choices' in data:
        print('✅ Mistral Response:', data['choices'][0]['message']['content'][:50] + '...')
    else:
        print('❌ Mistral Error:', data.get('error', {}).get('message', 'Unknown error'))
except Exception as e:
    print('❌ Mistral failed:', str(e))
"

echo ""

# Check channel status
echo "Channel Status:"
curl -s http://localhost:8000/api/v1/webhooks/channels/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for channel, details in data['channel_details'].items():
        status = '✅' if details['active'] else '❌'
        print(f'{status} {channel.title()}: {\"Connected\" if details[\"active\"] else \"Disconnected\"}')
except:
    print('❌ Could not get channel status')
"

echo ""
echo "💡 Next Steps:"
echo "1. If Ollama works but system fails: Check LLM gateway configuration"
echo "2. If Mistral fails: Check API key and billing"
echo "3. For email setup: Follow SETUP_GUIDE.md"