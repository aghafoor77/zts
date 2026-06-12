#!/bin/bash

# IoT Data Lake System - Setup Script
# This script sets up the development environment

set -e

echo "=========================================="
echo "IoT Data Lake System - Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

echo "✓ pip3 found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env file with your configuration"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Ensure MongoDB is running"
echo "3. Ensure Mosquitto MQTT broker is running"
echo "4. Run 'source venv/bin/activate' to activate virtual environment"
echo "5. Run 'python run_gateway.py' to start the Gateway"
echo "6. Run 'python -m consumer_gateway.consumer_gateway' to start the API"
echo "7. Run 'python run_sensor.py' to start a test sensor"
echo "8. Run 'python -m cli.cli interactive' to use the CLI"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up -d"
echo ""

# Made with # Com 
