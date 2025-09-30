#!/bin/bash

# Load environment variables and start containers with proper environment passing
echo "🔧 Loading environment and starting containers..."

# Source the environment file
set -a  # automatically export all variables
source .env.poc
set +a  # stop automatically exporting

echo "✅ Environment variables loaded"
echo "🚀 Starting containers..."

# Start containers
docker compose -f docker-compose.poc.yml up -d

echo "📊 Container status:"
docker compose -f docker-compose.poc.yml ps

echo ""
echo "🎯 Ready to test!"
echo "📱 Dashboard: http://localhost:8000/ui/"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""