#!/bin/bash
# Setup Conda Environment for IoT Data Lake CLI
# This script creates a conda environment and installs all dependencies

set -e

echo "=========================================="
echo "IoT Data Lake CLI - Conda Environment Setup"
echo "=========================================="

# Environment name
ENV_NAME="iot-cli"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo ""
echo "Step 1: Creating conda environment '$ENV_NAME' with Python 3.11..."
conda create -n $ENV_NAME python=3.11 -y

echo ""
echo "Step 2: Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

echo ""
echo "Step 3: Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To use the CLI, activate the environment:"
echo "  conda activate $ENV_NAME"
echo ""
echo "Then run CLI commands:"
echo "  python cli/cli.py --help"
echo "  python cli/cli.py interactive"
echo ""
echo "To deactivate the environment:"
echo "  conda deactivate"
echo ""

# Made with Bob