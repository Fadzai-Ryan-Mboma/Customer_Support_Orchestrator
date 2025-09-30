# 📡 CASSAVA AI - Channel Setup Guide

This guide helps you configure communication channels for your Cassava AI Support system.

## 🚀 Quick Setup Commands

### For Telegram (Already Working! ✅)
Your Telegram bot is already connected as "Cassava Support Bot" (@cassava_support_bot)

### For Email Setup (Gmail)

#### Step 1: Get Gmail App Password
1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to Security → 2-Step Verification (must be enabled)
3. Go to App passwords: https://myaccount.google.com/apppasswords
4. Generate app password for "Mail"
5. Copy the 16-character password (like: `abcd efgh ijkl mnop`)

#### Step 2: Update Configuration
Edit your `docker-compose.poc.yml` file and replace these lines:

```yaml
# Find these lines in docker-compose.poc.yml:
- EMAIL_USERNAME=your-email@gmail.com
- EMAIL_PASSWORD=your-app-password

# Replace with your actual credentials:
- EMAIL_USERNAME=your-actual-email@gmail.com
- EMAIL_PASSWORD=your-16-char-app-password
```

#### Step 3: Restart Services
```bash
cd /Users/fadzai/Documents/Cassava\ Code/Customer_Support_Orchestrator
docker compose -f docker-compose.poc.yml down
docker compose -f docker-compose.poc.yml up -d
```

#### Step 4: Test Email
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/channels/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your-test-email@gmail.com",
    "subject": "Test from Cassava AI",
    "message": "This is a test message from your Cassava AI Support system!"
  }'
```

## 🔧 Alternative Email Providers

### Outlook/Office365
```yaml
- EMAIL_SMTP_HOST=smtp.office365.com
- EMAIL_SMTP_PORT=587
- EMAIL_IMAP_HOST=outlook.office365.com
- EMAIL_IMAP_PORT=993
- EMAIL_USERNAME=your-email@outlook.com
- EMAIL_PASSWORD=your-password
```

### Custom SMTP Server
```yaml
- EMAIL_SMTP_HOST=your-smtp-server.com
- EMAIL_SMTP_PORT=587
- EMAIL_IMAP_HOST=your-imap-server.com
- EMAIL_IMAP_PORT=993
- EMAIL_USERNAME=your-username
- EMAIL_PASSWORD=your-password
```

## 🧪 Testing Your Channels

### Test All Channels
```bash
curl -s http://localhost:8000/api/v1/webhooks/channels/test | python3 -m json.tool
```

### Test Specific Channel
```bash
# Test Telegram
curl -X POST http://localhost:8000/api/v1/webhooks/channels/telegram/send \
  -H "Content-Type: application/json" \
  -d '{"to": "YOUR_TELEGRAM_CHAT_ID", "message": "Test from Cassava AI"}'

# Test Email  
curl -X POST http://localhost:8000/api/v1/webhooks/channels/email/send \
  -H "Content-Type: application/json" \
  -d '{"to": "test@example.com", "message": "Test email"}'
```

### Check Channel Status
```bash
curl -s http://localhost:8000/api/v1/webhooks/channels/status | python3 -m json.tool
```

## 🔑 Security Best Practices

1. **Never commit real credentials to Git**
2. **Use App Passwords, not account passwords**
3. **Rotate credentials regularly**
4. **Use environment variables in production**
5. **Enable 2FA on all accounts**

## 📞 Getting Your Telegram Chat ID

To send test messages to yourself on Telegram:

1. Message your bot: https://t.me/cassava_support_bot
2. Send any message to the bot
3. Check logs: `docker logs cassava-ai-poc --tail 10`
4. Look for your chat ID in the logs

## 🆘 Troubleshooting

### Email Not Working?
- Check App Password is correct (16 characters, no spaces)
- Verify 2FA is enabled on Google account
- Try connecting with a mail client first to test credentials
- Check firewall/network restrictions

### Telegram Not Responding?
- Verify bot token is correct
- Check bot is not blocked
- Ensure webhook URL is accessible (if using webhooks)

### AI Models Not Working?
- Run diagnostic: `./diagnostic.sh`
- Check Mistral API subscription
- Install Ollama models for fallback

## 🎯 Production Deployment

For production, use environment variables instead of hardcoding:

```yaml
# Production docker-compose.yml
environment:
  - EMAIL_USERNAME=${EMAIL_USERNAME}
  - EMAIL_PASSWORD=${EMAIL_PASSWORD}
  - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
```

Create `.env` file:
```bash
EMAIL_USERNAME=your-email@company.com
EMAIL_PASSWORD=your-app-password
TELEGRAM_BOT_TOKEN=your-bot-token
```

---

**Need help?** Run the diagnostic script: `./diagnostic.sh`