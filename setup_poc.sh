#!/bin/bash
set -e

echo "🚀 Setting up Cassava Support Orchestrator - PoC (Clean Structure)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Docker
command -v docker >/dev/null 2>&1 || { 
    print_error "Docker required but not installed. Please install Docker first."
    exit 1
}

# Check Docker Compose (both old and new syntax)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose required (neither 'docker-compose' nor 'docker compose' found)"
    exit 1
fi

print_status "Using Docker Compose command: $DOCKER_COMPOSE_CMD"
print_status "Checking prerequisites..."

# Check if we're in the correct directory
if [ ! -f "docker-compose.poc.yml" ]; then
    print_error "docker-compose.poc.yml not found. Please run this script from the project root directory."
    exit 1
fi

# Check backend directory structure
if [ ! -d "backend" ]; then
    print_error "Backend directory not found. Please ensure the project structure is correct."
    exit 1
fi

if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found. Please ensure the project structure is correct."
    exit 1
fi

# Create backend environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    print_status "Creating backend/.env file..."
    cat > backend/.env << EOF
# Environment Configuration
ENVIRONMENT=poc
DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# AI Models Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2

# Messaging Platforms (Optional - for webhook integration)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/webhooks/telegram
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token_here

# Database and Storage
DATABASE_URL=postgresql://user:password@postgres:5432/support_db
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
WEBHOOK_SECRET=dev-webhook-secret-change-in-production

# API Configuration
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*
EOF
    print_warning "Created backend/.env with placeholder values. Please update with your actual API keys."
else
    print_status "Backend environment file already exists."
fi

# Stop any existing containers to avoid port conflicts
print_status "Stopping any existing containers..."
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml down 2>/dev/null || true
$DOCKER_COMPOSE_CMD down 2>/dev/null || true

# Clean up any orphaned containers
docker container prune -f 2>/dev/null || true

# Build and start services
print_status "Building Docker images..."
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml build --no-cache

print_status "Starting services..."
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 20

# Check if Ollama is running and pull models
print_status "Setting up Ollama AI models..."
MAX_RETRIES=8
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml exec -T ollama ollama list >/dev/null 2>&1; then
        print_status "Ollama is ready. Pulling llama2 model..."
        $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml exec -T ollama ollama pull llama2 || {
            print_warning "Failed to pull llama2 model. Ollama fallback may not work properly."
        }
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        print_status "Waiting for Ollama to be ready... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 5
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_warning "Ollama not ready after $MAX_RETRIES attempts. Continuing anyway..."
fi

# Health check for main application
print_status "Checking application health..."
HEALTH_RETRIES=8
HEALTH_COUNT=0

while [ $HEALTH_COUNT -lt $HEALTH_RETRIES ]; do
    if curl -f http://localhost:8000/api/v1/ready > /dev/null 2>&1; then
        print_success "Application is healthy and ready!"
        break
    fi
    if [ $HEALTH_COUNT -eq $((HEALTH_RETRIES - 1)) ]; then
        print_warning "Health check timeout. Application may still be starting up."
        print_status "You can check logs with: $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml logs"
        break
    fi
    HEALTH_COUNT=$((HEALTH_COUNT + 1))
    sleep 2
done

# Display service status
print_status "Service Status:"
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml ps

print_success "✅ Cassava Support Orchestrator PoC is ready!"

echo ""
echo "🌐 Access Points:"
echo "   • Dashboard UI:        http://localhost:8000/ui/"
echo "   • API Documentation:   http://localhost:8000/docs"
echo "   • Health Check:        http://localhost:8000/api/v1/ready"
echo "   • System Status:       http://localhost:8000/api/v1/status"
echo "   • Ollama (AI Fallback): http://localhost:11434"

echo ""
echo "📁 Project Structure:"
echo "   • Backend Code:        ./backend/"
echo "   • Frontend Code:       ./frontend/"
echo "   • Environment Config:  ./backend/.env"
echo "   • Test Scripts:        ./bloat/"

echo ""
echo "🔧 Configuration:"
if [ -f "backend/.env" ]; then
    if grep -q "your_mistral_api_key_here" backend/.env; then
        print_warning "⚠️  Please update backend/.env with your actual API keys:"
        echo "   • MISTRAL_API_KEY (required for AI classification)"
        echo "   • TELEGRAM_BOT_TOKEN (optional, for Telegram integration)"
        echo "   • WHATSAPP_ACCESS_TOKEN (optional, for WhatsApp integration)"
    else
        print_success "Environment configuration looks good!"
    fi
fi

echo ""
echo "🧪 Testing:"
echo "   • Run AI tests:        cd bloat && python test_ai_consistency.py"
echo "   • Test single message: curl -X POST http://localhost:8000/api/v1/test/test -H 'Content-Type: application/json' -d '{\"message\":\"Test message\",\"customer_id\":\"test\",\"channel\":\"test\"}'"

echo ""
echo "🛠️  Management Commands:"
echo "   • View logs:           $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml logs -f"
echo "   • Stop services:       $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml down"
echo "   • Restart services:    $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml restart"
echo "   • Rebuild everything:  $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml up --build -d"

echo ""
echo "🎯 Next Steps:"
echo "   1. Update backend/.env with your API keys"
echo "   2. Visit the dashboard at http://localhost:8000/ui/"
echo "   3. Test the API at http://localhost:8000/docs"
echo "   4. Configure webhooks for your messaging platforms"

echo ""
print_success "Setup completed successfully! 🎉"
print_status "Happy coding! 🚀"