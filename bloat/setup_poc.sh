#!/bin/bash
set -e

echo "🚀 Setting up Cassava Support Orchestrator - PoC"

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
    print_error "Docker required"
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

# Check environment
if [ ! -f .env.poc ]; then
    print_status "Creating .env.poc file..."
    cat > .env.poc << EOF
# Mistral API Configuration
MISTRAL_API_KEY=your_mistral_api_key_here

# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Environment
ENVIRONMENT=poc
DEBUG=true
EOF
    print_warning "Created .env.poc with placeholder values. Please update with your actual API keys."
else
    print_status ".env.poc file already exists."
fi

# Load environment variables from .env.poc
print_status "Loading environment variables from .env.poc..."
set -a  # automatically export all variables
source .env.poc
set +a  # disable automatic export

# Build and start
print_status "Building Docker images..."
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml build

print_status "Starting services..."
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml up -d

# Wait for services
print_status "Waiting for services to start..."
sleep 15

# Pull Ollama models
print_status "Pulling Ollama models (this may take a while)..."
$DOCKER_COMPOSE_CMD -f docker-compose.poc.yml exec -T ollama ollama pull llama2:7b || {
    print_warning "Failed to pull llama2:7b model. Ollama fallback may not work."
}

# Health check
print_status "Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Application is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Health check failed"
        exit 1
    fi
    sleep 2
done

print_success "✅ Cassava Support Orchestrator PoC is ready!"

echo ""
echo "🔗 Service URLs:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo "   • Ollama: http://localhost:11434"

echo ""
echo "📝 Next Steps:"
echo "   1. Update your .env.poc file with actual API keys"
echo "   2. Visit http://localhost:8000/docs to explore the API"
echo "   3. Test webhook endpoints for WhatsApp/Telegram integration"

echo ""
echo "🛠️  Useful Commands:"
echo "   • View logs: $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml logs -f"
echo "   • Stop services: $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml down"
echo "   • Rebuild: $DOCKER_COMPOSE_CMD -f docker-compose.poc.yml up --build -d"

echo ""
print_success "Setup completed successfully! 🎉"