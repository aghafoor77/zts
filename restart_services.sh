#!/bin/bash

echo "Restarting services to apply trust metadata fix..."
echo "=" * 60

# Stop services
echo "Stopping services..."
docker compose stop gateway consumer_gateway 2>/dev/null || docker-compose stop gateway consumer_gateway

# Rebuild services
echo "Rebuilding services..."
docker compose build gateway consumer_gateway 2>/dev/null || docker-compose build gateway consumer_gateway

# Start services
echo "Starting services..."
docker compose up -d gateway consumer_gateway 2>/dev/null || docker-compose up -d gateway consumer_gateway

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check status
echo ""
echo "Service status:"
docker compose ps gateway consumer_gateway 2>/dev/null || docker-compose ps gateway consumer_gateway

echo ""
echo "=" * 60
echo "Services restarted! Trust metadata will now be preserved."
echo ""
echo "To verify:"
echo "1. Check gateway logs: docker compose logs gateway"
echo "2. Check consumer gateway logs: docker compose logs consumer_gateway"
echo "3. Query data: python -m cli.cli query-data --profile-id <id> --show-trust"
echo "4. Check web interface: http://localhost:3000"

# Made with Bob
