#!/bin/bash

# Cassava AI Support - AI Models & Channels Diagnostic Script
# This script helps you diagnose and test your AI models and communication channels

echo "🔍 CASSAVA AI DIAGNOSTIC TOOL"
echo "================================"
echo "Testing AI models and channel integrations..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if services are running
echo "📋 Step 1: Checking Service Status"
echo "--------------------------------"

if curl -s http://localhost:8000/api/v1/ready > /dev/null; then
    echo -e "${GREEN}✅ Main service is running${NC}"
    HEALTH=$(curl -s http://localhost:8000/api/v1/ready | python3 -c "import sys, json; print(json.load(sys.stdin)['ready'])")
    echo "   Service health: $HEALTH"
else
    echo -e "${RED}❌ Main service is not accessible${NC}"
    echo "   Please run: docker compose -f docker-compose.poc.yml up -d"
    exit 1
fi

if curl -s http://localhost:11434/api/version > /dev/null; then
    echo -e "${GREEN}✅ Ollama service is running${NC}"
    OLLAMA_VERSION=$(curl -s http://localhost:11434/api/version | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")
    echo "   Ollama version: $OLLAMA_VERSION"
else
    echo -e "${RED}❌ Ollama service is not accessible${NC}"
fi

echo ""

# Check AI Models
echo "🤖 Step 2: Testing AI Models"
echo "----------------------------"

echo "Testing Mistral AI (Primary):"
MISTRAL_TEST=$(curl -s -X POST http://localhost:8000/api/v1/test/llm \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, test message", "provider": "mistral"}')

if echo "$MISTRAL_TEST" | grep -q '"error"'; then
    echo -e "${RED}❌ Mistral AI Failed${NC}"
    echo "   Error: $(echo "$MISTRAL_TEST" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "Connection failed")"
    
    # Check API key
    if docker exec cassava-ai-poc printenv MISTRAL_API_KEY | grep -q "YFRSBgX6weJXLOrb7Hg2oy89Mc11fPa5"; then
        echo -e "${YELLOW}   💡 API Key is set but may be invalid or expired${NC}"
        echo -e "${BLUE}   📝 Action: Check your Mistral AI subscription at https://console.mistral.ai/${NC}"
    else
        echo -e "${RED}   💡 API Key missing or incorrect${NC}"
    fi
else
    echo -e "${GREEN}✅ Mistral AI Working${NC}"
    echo "   Response: $(echo "$MISTRAL_TEST" | python3 -c "import sys, json; print(json.load(sys.stdin).get('response', 'Success')[:50] + '...')" 2>/dev/null)"
fi

echo ""
echo "Testing Ollama (Fallback):"

# Check if models are available
OLLAMA_MODELS=$(curl -s http://localhost:11434/api/tags)
if echo "$OLLAMA_MODELS" | grep -q '"models"'; then
    MODEL_COUNT=$(echo "$OLLAMA_MODELS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['models']))" 2>/dev/null)
    if [ "$MODEL_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Ollama has $MODEL_COUNT model(s) installed${NC}"
        echo "   Available models:"
        echo "$OLLAMA_MODELS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for model in data['models']:
    print(f'   - {model[\"name\"]} (Size: {model[\"size\"]//1000000}MB)')
" 2>/dev/null
        
        # Test Ollama
        OLLAMA_TEST=$(curl -s -X POST http://localhost:8000/api/v1/test/llm \
          -H "Content-Type: application/json" \
          -d '{"message": "Hello, test message", "provider": "ollama"}')
        
        if echo "$OLLAMA_TEST" | grep -q '"error"'; then
            echo -e "${RED}❌ Ollama Test Failed${NC}"
            echo "   Error: $(echo "$OLLAMA_TEST" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null)"
        else
            echo -e "${GREEN}✅ Ollama Working${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Ollama running but no models installed${NC}"
        echo -e "${BLUE}   📝 Action: Install a model with: docker exec ollama-ai-poc ollama pull llama2${NC}"
    fi
else
    echo -e "${RED}❌ Ollama not responding${NC}"
fi

echo ""

# Check Communication Channels
echo "📡 Step 3: Testing Communication Channels"
echo "----------------------------------------"

CHANNEL_STATUS=$(curl -s http://localhost:8000/api/v1/webhooks/channels/status)
if [ $? -eq 0 ]; then
    echo "Channel Status:"
    echo "$CHANNEL_STATUS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Total channels: {data[\"total_channels\"]}')
    print(f'Active channels: {len(data[\"active_channels\"])}')
    print()
    
    for channel, details in data['channel_details'].items():
        status = '✅' if details['active'] else '❌'
        print(f'{status} {channel.title()} Channel:')
        if details['active']:
            print('   Status: Connected')
            if 'connection' in details and 'bot_info' in details['connection']:
                bot_info = details['connection']['bot_info']
                print(f'   Bot: {bot_info.get(\"first_name\", \"Unknown\")} (@{bot_info.get(\"username\", \"unknown\")})')
        else:
            if 'connection' in details and 'errors' in details['connection']:
                for error in details['connection']['errors'][:1]:  # Show first error only
                    print(f'   Error: {error[:80]}...')
            elif 'connection' in details and 'error' in details['connection']:
                print(f'   Error: {details[\"connection\"][\"error\"][:80]}...')
        print()
except Exception as e:
    print(f'Error parsing channel status: {e}')
"
else
    echo -e "${RED}❌ Could not get channel status${NC}"
fi

echo ""

# Recommendations
echo "💡 Step 4: Recommendations & Next Steps"
echo "--------------------------------------"

echo -e "${BLUE}AI Models:${NC}"
echo "1. If Mistral AI is failing:"
echo "   - Check your API key at https://console.mistral.ai/"
echo "   - Verify your subscription is active"
echo "   - Check billing status"
echo ""
echo "2. If Ollama needs models:"
echo "   - Run: docker exec ollama-ai-poc ollama pull llama2"
echo "   - Or try: docker exec ollama-ai-poc ollama pull llama3.2:1b"
echo ""

echo -e "${BLUE}Communication Channels:${NC}"
echo "1. For Telegram (if failing):"
echo "   - Get bot token from @BotFather on Telegram"
echo "   - Update TELEGRAM_BOT_TOKEN in docker-compose.poc.yml"
echo ""
echo "2. For Email setup:"
echo "   - Use Gmail App Password (not regular password)"
echo "   - Update EMAIL_USERNAME and EMAIL_PASSWORD in docker-compose.poc.yml"
echo ""

echo -e "${GREEN}🎉 Diagnostic complete!${NC}"
echo ""
echo "For detailed setup guides, run:"
echo "  curl -s http://localhost:8000/api/v1/test/help"