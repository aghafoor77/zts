# Quick Start Guide

Get the IoT Data Lake System up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+ with MongoDB and Mosquitto

## Option 1: Docker Compose (Easiest)

### 1. Deploy the System

```bash
./deploy.sh
```

This will:
- Build all Docker images
- Start MongoDB, Mosquitto, Gateway, Consumer Gateway, and a test sensor
- Verify all services are healthy

### 2. Verify Services

```bash
# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Use the CLI

```bash
# Install CLI dependencies (if not using Docker)
pip install -r requirements.txt

# Check system health
python -m cli.cli health

# List available profiles (wait 30 seconds for sensor to send data)
python -m cli.cli list-profiles

# Interactive mode
python -m cli.cli interactive
```

### 4. Query Data

```bash
# List schemas
python -m cli.cli list-schemas

# Query data (replace <profile_id> with actual ID from list-profiles)
python -m cli.cli query-data --profile-id <profile_id> --start-time 1h
```

## Option 2: Manual Setup

### 1. Setup Environment

```bash
./setup.sh
source venv/bin/activate
```

### 2. Start Services Manually

Terminal 1 - Gateway:
```bash
python run_gateway.py
```

Terminal 2 - Consumer Gateway:
```bash
python -m consumer_gateway.consumer_gateway
```

Terminal 3 - Test Sensor:
```bash
python run_sensor.py
```

Terminal 4 - CLI:
```bash
python -m cli.cli interactive
```

## Testing the System

### 1. Check Health

```bash
curl http://localhost:5000/health
```

Expected output:
```json
{
  "status": "healthy",
  "service": "Consumer Gateway"
}
```

### 2. Wait for Data

The test sensor sends data every 10 seconds. Wait about 30 seconds, then:

```bash
# List available profiles
curl http://localhost:5000/api/profiles
```

### 3. Query Data via API

```bash
# Get schemas
curl http://localhost:5000/api/schemas

# Get data for a profile (replace PROFILE_ID)
curl "http://localhost:5000/api/data/profile/PROFILE_ID?limit=10"
```

### 4. Query Data via CLI

```bash
# Interactive mode (easiest)
python -m cli.cli interactive

# Or direct commands
python -m cli.cli list-profiles
python -m cli.cli query-data --profile-id PROFILE_ID --start-time 1h
```

## Example Workflow

```bash
# 1. Deploy system
./deploy.sh

# 2. Wait 30 seconds for sensor to send data
sleep 30

# 3. Check available profiles
python -m cli.cli list-profiles

# Output example:
# Available Profiles (1):
# 1. a1b2c3d4e5f6g7h8

# 4. Query data for the profile
python -m cli.cli query-data --profile-id a1b2c3d4e5f6g7h8 --start-time 1h --format table

# 5. View in JSON format
python -m cli.cli query-data --profile-id a1b2c3d4e5f6g7h8 --start-time 1h --format json
```

## Creating Your Own Sensor

```python
from sensor.sensor import Sensor
import time

# Create sensor
sensor = Sensor(
    sensor_id="my_sensor_001",
    device_type="sensor",
    manufacturer="MyCompany",
    model="Model-X",
    certificate="VALID_CERTIFICATE_XYZ"
)

# Connect
sensor.connect()
time.sleep(3)  # Wait for profile

# Send data
sensor.send_data({
    "temperature": 25.5,
    "humidity": 60.0,
    "custom_field": "value"
})

# Disconnect
sensor.disconnect()
```

## Stopping the System

### Docker Compose:
```bash
docker-compose down
```

### Manual:
Press `Ctrl+C` in each terminal running a service.

## Troubleshooting

### Services not starting?
```bash
# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart gateway
```

### No data appearing?
```bash
# Check sensor logs
docker-compose logs sensor_simulator

# Check gateway logs
docker-compose logs gateway

# Verify MongoDB has data
docker-compose exec mongodb mongosh
use iot_data_lake
db.sensor_data.find().limit(5)
```

### CLI not connecting?
```bash
# Verify Consumer Gateway is running
curl http://localhost:5000/health

# Check if port 5000 is available
netstat -an | grep 5000
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [API Documentation](README.md#api-documentation)
- Customize sensor data generation
- Add authentication and security
- Scale with multiple sensors

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Review [README.md](README.md) troubleshooting section