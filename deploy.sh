#!/bin/bash

# IoT Data Lake System - Deployment Script
# This script deploys the system using Docker Compose

set -e

echo "=========================================="
echo "IoT Data Lake System - Deployment"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker Compose found: $(docker-compose --version)"

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Using default configuration. Edit .env for custom settings."
fi

# Stop any running containers
echo ""
echo "Stopping any running containers..."
docker-compose down 2>/dev/null || true

# Build images
echo ""
echo "Building Docker images..."
docker-compose build

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service status
echo ""
echo "Checking service status..."
docker-compose ps

# Test Consumer Gateway health
echo ""
echo "Testing Consumer Gateway health..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "✓ Consumer Gateway is healthy"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Waiting for Consumer Gateway... ($retry_count/$max_retries)"
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "⚠ Consumer Gateway health check timed out"
    echo "Check logs with: docker-compose logs consumer_gateway"
fi

echo ""
echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  - MongoDB:           localhost:27017"
echo "  - MQTT Broker:       localhost:1883"
echo "  - Consumer Gateway:  http://localhost:5000"
echo "  - Gateway:           Running in background"
echo "  - Sensor Simulator:  Running in background"
echo ""
echo "Useful commands:"
echo "  View logs:           docker-compose logs -f"
echo "  Stop services:       docker-compose down"
echo "  Restart services:    docker-compose restart"
echo "  View status:         docker-compose ps"
echo ""
echo "Using the CLI:"
echo "  Health check:        python -m cli.cli health"
echo "  List schemas:        python -m cli.cli list-schemas"
echo "  Interactive mode:    python -m cli.cli interactive"
echo ""
echo "API Documentation:"
echo "  Health:              curl http://localhost:5000/health"
echo "  Schemas:             curl http://localhost:5000/api/schemas"
echo "  Profiles:            curl http://localhost:5000/api/profiles"
echo ""

# Made with Bob
