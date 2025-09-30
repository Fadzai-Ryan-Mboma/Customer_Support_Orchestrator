#!/bin/bash
# Quick fix for environment variable loading

echo "🔧 Fixing environment variable loading..."

# Load environment variables
set -a
source .env.poc
set +a

echo "✅ Environment variables loaded:"
echo "   MISTRAL_API_KEY: ${MISTRAL_API_KEY:0:8}..."
echo "   TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:8}..."

# Restart with proper environment
echo "🔄 Restarting containers with environment..."
docker compose -f docker-compose.poc.yml down
docker compose -f docker-compose.poc.yml up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Test the fix
echo "🧪 Testing AI processing..."
curl -X POST http://localhost:8000/api/v1/test/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message for API check", "customer_id": "test", "channel": "test"}' \
  | jq .

echo "✅ Environment fix completed!"