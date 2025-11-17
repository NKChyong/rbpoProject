#!/bin/bash
# Quick start script for Reading List API

set -e

echo "🚀 Reading List API - Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt -r requirements-dev.txt

# Start PostgreSQL
echo ""
echo "🐘 Starting PostgreSQL..."
docker-compose up -d db

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed data (optional)
read -p "📊 Do you want to load sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Loading sample data..."
    python scripts/seed_data.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 You can now start the application:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📚 API Documentation:"
echo "   http://localhost:8000/api/docs"
echo ""
echo "🧪 Run tests:"
echo "   pytest"
echo ""
echo "🛠  Sample credentials (if you loaded sample data):"
echo "   User: alice / Alic3Strong!45"
echo "   Admin: admin / AdminSecur3!45"
echo ""
