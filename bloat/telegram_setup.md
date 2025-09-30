# 🤖 Telegram Bot Setup Guide

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the prompts to create your bot:
   - Choose a name for your bot (e.g., "Cassava Support Bot")
   - Choose a username ending in 'bot' (e.g., "cassava_support_bot")
4. BotFather will provide you with a bot token - save this!

## Step 2: Configure Environment Variables

1. Edit `.env.poc` file
2. Replace `your_telegram_bot_token_here` with your actual bot token
3. Update the webhook URL to match your domain/ngrok URL

## Step 3: Set Up Webhook (for production)

```bash
# Replace with your actual bot token and webhook URL
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://your-domain.com/api/v1/webhooks/telegram",
       "allowed_updates": ["message", "callback_query"]
     }'
```

## Step 4: Test Your Bot

1. Start the application: `docker-compose -f docker-compose.poc.yml up`
2. Open the web dashboard: `http://localhost:8000/ui/`
3. Use the "Live AI Test" section to test responses
4. Search for your bot on Telegram and send a test message

## Step 5: Local Testing with ngrok (optional)

If you want to test webhooks locally:

```bash
# Install ngrok and expose port 8000
ngrok http 8000

# Use the ngrok URL in your webhook configuration
# Example: https://abc123.ngrok.io/api/v1/webhooks/telegram
```

## Testing Commands

Test these messages with your bot:
- "My payment failed!"
- "I need help with my order"
- "How do I reset my password?"
- "I want to cancel my subscription"

The AI should classify these messages and provide appropriate responses!