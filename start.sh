#!/bin/bash

# LLM Chat Platform Startup Script

set -e

echo "========================================="
echo "LLM Chat Platform Startup"
echo "========================================="

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo ""
    echo "⚠️  Please edit backend/.env and add your API keys!"
    echo "⚠️  You can generate an encryption key with:"
    echo "    python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    echo ""
    read -p "Press enter to continue once you've configured .env file..."
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p backend/data backend/uploads backend/logs

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Build and start containers
echo ""
echo "Building and starting containers..."
docker-compose down
docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to start..."
sleep 10

# Check backend health
echo "Checking backend health..."
if curl -f http://localhost:3211/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed, but service may still be starting..."
fi

echo ""
echo "========================================="
echo "✅ LLM Chat Platform is running!"
echo "========================================="
echo ""
echo "Backend API:  http://localhost:3211"
echo "Frontend UI:  http://localhost:3212"
echo "API Docs:     http://localhost:3211/docs"
echo ""
echo "To view logs:     docker-compose logs -f"
echo "To stop:          docker-compose down"
echo "To restart:       docker-compose restart"
echo ""
echo "========================================="
