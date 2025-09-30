# Customer Support Orchestrator

AI-powered multi-channel customer support system with intelligent classification and response generation.

## 🏗️ Project Structure

```
Customer_Support_Orchestrator/
├── backend/                    # FastAPI backend application
│   ├── app/                   # Main application code
│   │   ├── agents/           # AI agent orchestration
│   │   ├── api/              # REST API endpoints
│   │   ├── core/             # Core business logic
│   │   └── main.py           # FastAPI application
│   ├── Dockerfile            # Backend container configuration
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/                  # Web dashboard UI
│   └── index.html            # Customer support dashboard
├── docker-compose.yml        # Production container orchestration
├── docker-compose.poc.yml    # Development container setup
└── README.md                 # This file
```

## 🚀 Quick Start

### Development Setup
```bash
# Start the development environment
docker compose -f docker-compose.poc.yml up --build

# Or use the clean production setup
docker compose up --build
```

### Access Points
- **Dashboard**: http://localhost:8000/ui/
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/ready

## 🎯 Features

- **Multi-Channel Support**: Telegram and Email integration
- **Intelligent AI Classification**: Automatic priority and category detection  
- **Smart Response Generation**: Context-aware customer responses
- **Real-time Dashboard**: Dark/light theme support with Cassava branding
- **AI Fallback System**: Mistral primary, Ollama local fallback
- **Professional UI**: Clean white/grey design with dynamic logo switching

## 🔧 Configuration

1. Environment variables are configured in `docker-compose.poc.yml`
2. For email setup, update credentials in the compose file:
```yaml
- EMAIL_USERNAME=your-email@gmail.com
- EMAIL_PASSWORD=your-gmail-app-password
```
3.Credeentials/keys are configured in `.env`
1. For setup, update credentials/keys in the compose file:
```yaml
MISTRAL_API_KEY=your token
TELEGRAM_BOT_TOKEN=your token
```

## 🏃‍♂️ Running the Application

### Quick Start
```bash
# Start POC environment
docker compose -f docker-compose.poc.yml up --build

# Or use the setup script
./setup_poc.sh
```

### Testing & Diagnostics
```bash
# Test all systems
./diagnostic.sh

# Quick AI/channel test
./quick_test.sh
```

The system consists of:
- **Backend**: FastAPI application with unified channel management
- **Frontend**: Single-page dashboard with Cassava branding
- **AI Models**: Mistral API primary, Ollama (llama3.2:1b) fallback
- **Channels**: Telegram Bot and Email service

## 📱 Supported Channels

- **Telegram**: Bot API integration (✅ Active)
- **Email**: SMTP/IMAP with auto-polling (⚠️ Needs credentials)
- **Webhook API**: Unified processing for all channels

## 🧪 Testing

- **Channel Status**: `GET /api/v1/webhooks/channels/status`
- **Test All Channels**: `POST /api/v1/webhooks/channels/test`
- **Web Dashboard**: http://localhost:8000/ui/


## 📄 License

Private project for Cassava Technologies.
