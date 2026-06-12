#!/bin/bash
# Wrapper script to run CLI from project root
# Ensures proper Python path for module imports

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project root directory
cd "$SCRIPT_DIR"

# Add project root to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the CLI with all arguments passed to this script
python cli/cli.py "$@"

# Made with Bob