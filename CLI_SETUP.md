# IoT Data Lake CLI - Conda Environment Setup

This guide explains how to set up a Conda virtual environment for running the CLI.

## Prerequisites

- **Conda** (Miniconda or Anaconda) installed
  - Download Miniconda: https://docs.conda.io/en/latest/miniconda.html
  - Or Anaconda: https://www.anaconda.com/download

## Quick Setup (Automated)

### Option 1: Using the Setup Script

```bash
# Make the script executable
chmod +x setup_conda_env.sh

# Run the setup script
./setup_conda_env.sh
```

This will:
1. Create a conda environment named `iot-cli` with Python 3.11
2. Install all required dependencies from `requirements.txt`
3. Display activation instructions

### Option 2: Using environment.yml

```bash
# Create environment from YAML file
conda env create -f environment.yml

# Activate the environment
conda activate iot-cli
```

## Manual Setup

If you prefer to set up manually:

```bash
# 1. Create a new conda environment
conda create -n iot-cli python=3.11 -y

# 2. Activate the environment
conda activate iot-cli

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import click, requests, tabulate; print('✓ All dependencies installed')"
```

## Using the CLI

### 1. Activate the Environment

Every time you want to use the CLI, first activate the conda environment:

```bash
conda activate iot-cli
```

### 2. Start the Docker Services

The CLI connects to the Consumer Gateway API, so ensure Docker services are running:

```bash
docker-compose up -d
```

Wait 30 seconds for sensors to start sending data.

### 3. Run CLI Commands

**Important**: Always run CLI from the project root directory!

```bash
# Make sure you're in the project root
cd /home/testbed/Desktop/ZTS

# Option 1: Using the wrapper script (recommended)
./run_cli.sh --help
./run_cli.sh health
./run_cli.sh interactive

# Option 2: Using Python directly from project root
python cli/cli.py --help
python cli/cli.py health
python cli/cli.py interactive

# List available profiles
./run_cli.sh list-profiles

# Query data
./run_cli.sh query-data --profile-id <profile_id> --start-time 1h
```

### 4. Deactivate When Done

```bash
conda deactivate
```

## CLI Commands Reference

### Health Check
```bash
./run_cli.sh health
# or: python cli/cli.py health
```

### List Schemas
```bash
./run_cli.sh list-schemas
```

### Show Specific Schema
```bash
./run_cli.sh show-schema <profile_id>
```

### List Profiles
```bash
./run_cli.sh list-profiles
```

### Query Data by Profile
```bash
# Basic query
./run_cli.sh query-data --profile-id <profile_id>

# With time range (last hour)
./run_cli.sh query-data --profile-id <profile_id> --start-time 1h

# With time range (last 24 hours)
./run_cli.sh query-data --profile-id <profile_id> --start-time 1d

# JSON output
./run_cli.sh query-data --profile-id <profile_id> --format json

# Limited results
./run_cli.sh query-data --profile-id <profile_id> --limit 50
```

### Query Data by Sensor
```bash
./run_cli.sh query-sensor --sensor-id sensor_001 --start-time 1h
```

### Interactive Mode
```bash
./run_cli.sh interactive
```

This provides a guided interface with prompts for:
- Profile selection
- Schema viewing
- Time range filtering
- Output format selection

## Time Format Examples

- `1h` - Last 1 hour
- `2h` - Last 2 hours
- `1d` - Last 1 day
- `30m` - Last 30 minutes
- `2026-06-11T10:00:00` - Specific ISO timestamp

## Environment Management

### List All Conda Environments
```bash
conda env list
```

### Remove the Environment
```bash
conda deactivate
conda env remove -n iot-cli
```

### Update Dependencies
```bash
conda activate iot-cli
pip install -r requirements.txt --upgrade
```

### Export Environment
```bash
conda activate iot-cli
conda env export > environment_backup.yml
```

## Troubleshooting

### Issue: "conda: command not found"
**Solution**: Install Conda or add it to your PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/miniconda3/bin:$PATH"
source ~/.bashrc
```

### Issue: "Error connecting to Consumer Gateway"
**Solution**: 
1. Check if Docker services are running: `docker-compose ps`
2. Verify Consumer Gateway is accessible: `curl http://localhost:5000/health`
3. Check config/config.py for correct host/port settings

### Issue: "No profiles available"
**Solution**: 
1. Wait 30-60 seconds after starting Docker services
2. Check if sensors are sending data: `docker-compose logs iot_sensor_simulator`
3. Verify Gateway is receiving data: `docker-compose logs gateway`

### Issue: "ModuleNotFoundError"
**Solution**: Ensure environment is activated and dependencies are installed:
```bash
conda activate iot-cli
pip install -r requirements.txt
```

## Complete Workflow Example

```bash
# 1. Setup (one-time)
./setup_conda_env.sh

# 2. Start Docker services
docker-compose up -d

# 3. Wait for data collection
sleep 30

# 4. Activate environment
conda activate iot-cli

# 5. Navigate to project root (if not already there)
cd /home/testbed/Desktop/ZTS

# 6. Use CLI
./run_cli.sh health
./run_cli.sh interactive

# 7. When done
conda deactivate
docker-compose down
```

## Dependencies Installed

The conda environment includes:
- **click** - CLI framework
- **requests** - HTTP client for API calls
- **tabulate** - Table formatting
- **python-dateutil** - Date/time parsing
- **paho-mqtt** - MQTT client (for future direct sensor access)
- **pymongo** - MongoDB driver (for future direct DB access)
- **flask** - Web framework (for Consumer Gateway)
- **cryptography** - Certificate handling
- And more (see requirements.txt)

## Additional Resources

- Conda Documentation: https://docs.conda.io/
- Click Documentation: https://click.palletsprojects.com/
- Project README: See README.md in project root

---

