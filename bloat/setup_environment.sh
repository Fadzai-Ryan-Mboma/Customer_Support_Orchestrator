#!/bin/bash

# Environment Setup Script for Customer Support Orchestrator
# This script ensures all environment variables are properly loaded in Docker containers

echo "🔧 Setting up environment variables for Docker containers..."

# Create .env.poc file if it doesn't exist
if [ ! -f .env.poc ]; then
    echo "📝 Creating .env.poc file with default configuration..."
    cat > .env.poc << 'EOF'
# ===========================================
# Customer Support Orchestrator - PoC Config
# ===========================================

# Application Settings
ENVIRONMENT=poc
DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# AI/LLM Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/webhooks/telegram

# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token_here

# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/support_db
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
WEBHOOK_SECRET=your-webhook-secret-key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
EOF
    echo "✅ Created .env.poc with default values"
    echo "⚠️  Please update API keys in .env.poc before starting containers"
fi

echo "✅ Environment setup script created!"
echo ""
echo "📋 Next Steps:"
echo "1. Run: chmod +x setup_environment.sh"
echo "2. Run: ./setup_environment.sh"
echo "3. Edit .env.poc to add your API keys"
echo "4. Follow telegram_setup.md to create a Telegram bot"
echo "5. Restart containers and test!"