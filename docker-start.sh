#!/bin/bash
# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

# Export variables for Docker
export COMPOSE_PROJECT_NAME=nl2sql_tool

# Start Docker Compose
echo "Starting NL2SQL Tool with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Display connection info
echo ""
echo "🚀 NL2SQL Tool is starting up!"
echo "🌐 Access the application at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "🐳 Docker Services:"
echo "  - NL2SQL API: Port 8000"
echo "  - Ollama: Port 11434"
echo "  - PostgreSQL: Port 5432"
echo ""
echo "To shut down: docker-compose down"
