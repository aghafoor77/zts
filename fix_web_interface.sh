#!/bin/bash

# Fix Web Interface - Rebuild with correct service name

echo "Fixing web interface nginx configuration..."

# Stop and remove the web interface container
docker compose stop web_interface 2>/dev/null || docker-compose stop web_interface
docker compose rm -f web_interface 2>/dev/null || docker-compose rm -f web_interface

# Rebuild the web interface
echo "Rebuilding web interface..."
docker compose build web_interface 2>/dev/null || docker-compose build web_interface

# Start the web interface
echo "Starting web interface..."
docker compose up -d web_interface 2>/dev/null || docker-compose up -d web_interface

# Wait a moment
sleep 3

# Check status
echo ""
echo "Checking status..."
docker compose ps web_interface 2>/dev/null || docker-compose ps web_interface

echo ""
echo "Web interface should now be available at: http://localhost:3000"
echo ""
echo "If you see errors, check logs with:"
echo "  docker compose logs web_interface"
echo "  or"
echo "  docker-compose logs web_interface"

# Made with Bob
