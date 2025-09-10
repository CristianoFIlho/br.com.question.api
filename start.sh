#!/bin/bash

# Salesforce Quiz API - Start Script

echo "🚀 Starting Salesforce Quiz API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python init_db.py

# Start the API server
echo "🌐 Starting API server..."
echo "📚 API Documentation will be available at: http://localhost:8000/docs"
echo "🔴 ReDoc will be available at: http://localhost:8000/redoc"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
