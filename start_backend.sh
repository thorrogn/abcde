#!/bin/bash

# Disaster Management Backend Startup Script

echo "🚀 Starting Disaster Management Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Navigate to backend directory
cd Backend

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if config files exist
if [ ! -f "gdacs_config.yaml" ]; then
    echo "⚠️  Warning: gdacs_config.yaml not found. Using default configuration."
fi

if [ ! -f "reliefweb_config.yaml" ]; then
    echo "⚠️  Warning: reliefweb_config.yaml not found. Using default configuration."
fi

# Start the application
echo "🌟 Starting Flask application..."
echo "📍 Backend will be available at: http://localhost:5000"
echo "📊 Metrics available at: http://localhost:5000/metrics"
echo "🔍 API endpoints:"
echo "   - Health: http://localhost:5000/api/health"
echo "   - Disasters: http://localhost:5000/api/disasters"
echo "   - Weather: http://localhost:5000/api/weather"
echo "   - Status: http://localhost:5000/api/status"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

python app.py
