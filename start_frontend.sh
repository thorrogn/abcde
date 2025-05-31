#!/bin/bash

# Disaster Management Frontend Startup Script

echo "🚀 Starting Disaster Management Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Navigate to frontend directory
cd Frontend

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Start the development server
echo "🌟 Starting development server..."
echo "📍 Frontend will be available at: http://localhost:5173"
echo "🔗 Make sure the backend is running at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

npm run dev
