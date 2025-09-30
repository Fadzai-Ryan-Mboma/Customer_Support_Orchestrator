# 🚀 Cassava Support Orchestrator - Webhook Integration Guide

## 🔧 Environment Variables Setup

Your `.env.poc` file should contain:
```bash
# Mistral API Configuration
MISTRAL_API_KEY=your_actual_mistral_key_here

# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Environment
ENVIRONMENT=poc
DEBUG=true
```

## 📱 WhatsApp Integration

### 1. Setup WhatsApp Business API
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app with WhatsApp Business API
3. Set up a webhook URL: `https://your-domain.com/api/v1/webhooks/whatsapp`

### 2. Configure Webhook Verification
Update the verification token in `app/api/v1/webhooks.py`:
```python
verify_token = "your_unique_verification_token"
```

### 3. Test WhatsApp Webhook
```bash
# Verification (GET request)
curl "http://localhost:8000/api/v1/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=your_verify_token&hub.challenge=test_challenge"

# Message processing (POST request)
curl -X POST http://localhost:8000/api/v1/webhooks/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "id": "msg_001",
            "from": "1234567890",
            "text": {"body": "I need help with billing"}
          }]
        }
      }]
    }]
  }'
```

## 🤖 Telegram Integration

### 1. Create Telegram Bot
1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Get your bot token
4. Set webhook: `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/api/v1/webhooks/telegram`

### 2. Test Telegram Webhook
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "API is not working properly",
      "from": {"id": "user123"},
      "chat": {"id": "chat123"}
    }
  }'
```

## 🧪 Testing AI Processing

### 1. Test Classification
```bash
curl -X POST http://localhost:8000/api/v1/test/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My payment failed!",
    "customer_id": "test_customer",
    "channel": "test"
  }'
```

### 2. Test Different Message Types
```bash
# Billing issue
curl -X POST http://localhost:8000/api/v1/test/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I was charged twice for my subscription",
    "customer_id": "customer_001",
    "channel": "whatsapp"
  }'

# Technical issue
curl -X POST http://localhost:8000/api/v1/test/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The API returns 500 errors when uploading files",
    "customer_id": "customer_002",
    "channel": "email"
  }'

# General inquiry
curl -X POST http://localhost:8000/api/v1/test/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What features are included in the pro plan?",
    "customer_id": "customer_003",
    "channel": "website"
  }'
```

## 📊 Analytics & Monitoring

### 1. Dashboard Metrics
```bash
curl "http://localhost:8000/api/v1/analytics/dashboard?tenant_id=your_tenant&days=7"
```

### 2. Conversation Management
```bash
# List conversations
curl "http://localhost:8000/api/v1/conversations/?tenant_id=your_tenant"

# Get specific conversation
curl "http://localhost:8000/api/v1/conversations/conv_123"
```

## 🔧 Environment Testing

### Test if environment variables are loaded:
```bash
# Check container environment
docker compose -f docker-compose.poc.yml exec cassava-poc env | grep -E "(MISTRAL|TELEGRAM)"
```

## 🚀 Production Deployment

### 1. Update Environment Variables
- Set real API keys in `.env.poc`
- Use environment-specific configuration

### 2. SSL/HTTPS Setup
- Use reverse proxy (nginx/traefik)
- Configure SSL certificates
- Update webhook URLs to use HTTPS

### 3. Database Integration
- Replace mock data with real database
- Add proper data persistence
- Implement conversation history

### 4. Monitoring & Logging
- Set up log aggregation
- Add metrics collection
- Configure alerting

## 📝 Customization

### 1. Add Custom Agents
Edit `app/agents/master_orchestrator.py` to add specialized agents for your business logic.

### 2. Extend API Endpoints
Add new endpoints in `app/api/v1/` for your specific needs.

### 3. Integrate with External Systems
- CRM integration
- Ticketing system integration  
- Payment processing
- Knowledge base integration

## 🛠️ Troubleshooting

### Common Issues:
1. **Environment variables not loading**: Check `.env.poc` file and Docker Compose configuration
2. **Mistral API errors**: Verify API key and network connectivity
3. **Ollama not responding**: Ensure Ollama container is running and models are downloaded
4. **Webhook verification fails**: Check verification token configuration

### Debug Commands:
```bash
# View logs
docker compose -f docker-compose.poc.yml logs -f

# Check container status
docker compose -f docker-compose.poc.yml ps

# Restart services
docker compose -f docker-compose.poc.yml restart

# Rebuild and restart
docker compose -f docker-compose.poc.yml up --build -d
```