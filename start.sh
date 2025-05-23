#!/bin/bash

echo "🚀 Starting NL2SQL Tool..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
echo "📋 Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
echo "📋 Checking Ollama service..."
if ! ollama list >/dev/null 2>&1; then
    echo "📋 Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Start the application
echo "📋 Starting NL2SQL Tool API..."
echo "🌐 The application will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
