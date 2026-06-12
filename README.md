# IoT Data Lake System

A comprehensive IoT data management system with MQTT-based sensor communication, encrypted data transmission, automatic schema generation, and CLI-based data access.

## Table of Contents

- [System Architecture](#system-architecture)
- [Components](#components)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## System Architecture

```
┌─────────┐         ┌─────────┐         ┌───────────┐         ┌──────────────────┐         ┌─────┐
│ Sensor  │ ──MQTT─→│ Gateway │ ──────→ │ Data Lake │ ←────── │ Consumer Gateway │ ←────── │ CLI │
│         │         │         │         │ (MongoDB) │         │    (REST API)    │         │     │
└─────────┘         └─────────┘         └───────────┘         └──────────────────┘         └─────┘
     │                   │                     │
     │                   │                     │
     └───── Profile ─────┘                     │
           Generation                          │
                                               │
                                        Schema Generation
```

### Workflow

1. **Sensor Connection**: Sensors connect to the Gateway via MQTT protocol
2. **Profile Generation**: Gateway collects device info and generates security profiles using Profile Store
3. **Authentication**: Sensors authenticate based on profile requirements
4. **Data Transmission**: Sensors send encrypted JSON data to Gateway
5. **Data Storage**: Gateway decrypts and stores data in MongoDB Data Lake
6. **Schema Generation**: System automatically generates JSON schemas from first data payload
7. **Data Access**: CLI queries data through Consumer Gateway REST API

## Components

### 1. Gateway
- **Purpose**: MQTT broker interface, profile management, data reception
- **Key Features**:
  - Handles sensor connections
  - Generates device profiles via Profile Store
  - Manages authentication
  - Decrypts incoming sensor data
  - Forwards data to Data Lake

### 2. Profile Store
- **Purpose**: Black-box component for device profile generation
- **Key Features**:
  - Verifies device certificates
  - Generates security profiles based on device characteristics
  - Calculates risk scores
  - Manages profile storage

### 3. Sensor
- **Purpose**: IoT device simulator
- **Key Features**:
  - MQTT client implementation
  - Profile-based authentication
  - AES encryption for data transmission
  - Configurable data generation

### 4. Data Lake
- **Purpose**: NoSQL storage with automatic schema generation
- **Key Features**:
  - MongoDB-based storage
  - Automatic JSON schema generation
  - Time-series data indexing
  - Profile-based data organization

### 5. Consumer Gateway
- **Purpose**: REST API for data access
- **Key Features**:
  - RESTful API endpoints
  - Schema retrieval
  - Time-range queries
  - Profile and sensor-based filtering

### 6. CLI
- **Purpose**: Command-line interface for data access
- **Key Features**:
  - Interactive mode
  - Schema browsing
  - Data querying with filters
  - Multiple output formats (table, JSON)
  - **Trust and traceability information display**
  - **Access log viewing for auditing**
  - **Full-text search across data**
  - **Schema-based field search**

### 7. Web Interface (NEW!)
- **Purpose**: Simple, production-ready web dashboard for data visualization and analytics
- **Key Features**:
  - **Zero Trust Security themed UI** with dark mode
  - **Interactive Dashboard** with real-time trust analytics
  - **Data Explorer** with profile-based data browsing
  - **Traceability Viewer** for access logs and audit trails
  - **Security Analytics** with trust score visualization
  - **Schema Browser** with expandable schema details
  - **Responsive Design** optimized for all devices
  - **Single-file HTML/JavaScript** - no build process required
  - **Nginx-based deployment** with API proxy
  - **Cybersecurity Focus** with trust indicators and color-coded alerts

## Features

- ✅ MQTT-based sensor communication
- ✅ Automatic device profile generation
- ✅ Certificate-based device verification
- ✅ AES encryption for data transmission
- ✅ Username/password authentication
- ✅ **Digital signatures for data trust**
- ✅ **Complete traceability with access logging**
- ✅ **Advanced search capabilities**
- ✅ Automatic JSON schema generation
- ✅ NoSQL data storage (MongoDB)
- ✅ RESTful API for data access
- ✅ Interactive CLI with multiple query options
- ✅ Docker Compose deployment
- ✅ Time-range data filtering
- ✅ Profile-based data organization

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+ with pip
- MongoDB 7.0+
- Eclipse Mosquitto MQTT Broker

## Installation

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd iot-data-lake-system
```

2. Start all services:
```bash
docker-compose up -d
```

3. Verify services are running:
```bash
docker-compose ps
```

### Option 2: Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install and start MongoDB:
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# macOS
brew install mongodb-community
brew services start mongodb-community
```

3. Install and start Mosquitto:
```bash
# Ubuntu/Debian
sudo apt-get install mosquitto
sudo systemctl start mosquitto

# macOS
brew install mosquitto
brew services start mosquitto
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# MongoDB Configuration
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB_NAME=iot_data_lake

# Consumer Gateway Configuration
CONSUMER_GATEWAY_HOST=0.0.0.0
CONSUMER_GATEWAY_PORT=5000

# Encryption Configuration
AES_KEY=YourSecretKey123  # Change this!
```

### Profile Schema

The system uses the following profile schema for device configuration:

```json
{
  "profileID": "unique_profile_id",
  "device_type": "sensor",
  "manufacturer": "TempCorp",
  "model": "TH-100",
  "message_type": "telemetry",
  "protocol": "MQTT",
  "firmware_version": 1.0,
  "supports_encryption": 1,
  "supports_authentication": 1,
  "secure_boot": 1,
  "update_frequency_days": 30,
  "required_encryption": 1,
  "required_authentication": 0,
  "required_key_rotation_days": 90,
  "recommended_protocol": 1,
  "risk_score": 0.3
}
```

## Usage

### Starting the System

#### With Docker Compose:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Manual Start:

1. Start Gateway:
```bash
python run_gateway.py
```

2. Start Consumer Gateway:
```bash
python -m consumer_gateway.consumer_gateway
```

3. Start Sensor (optional, for testing):
```bash
python run_sensor.py
```

### Using the CLI

#### Install CLI dependencies:
```bash
pip install -r requirements.txt
```

#### Check system health:
```bash
python -m cli.cli health
```

#### List available schemas:
```bash
python -m cli.cli list-schemas
```

#### Show specific schema:
```bash
python -m cli.cli show-schema <profile_id>
```

#### List available profiles:
```bash
python -m cli.cli list-profiles
```

#### Query data by profile:
```bash
# Basic query
python -m cli.cli query-data --profile-id <profile_id>

# With time range (last hour)
python -m cli.cli query-data --profile-id <profile_id> --start-time 1h

# With custom limit
python -m cli.cli query-data --profile-id <profile_id> --limit 50

# JSON output
python -m cli.cli query-data --profile-id <profile_id> --format json
```

#### Query data by sensor:
```bash
python -m cli.cli query-sensor --sensor-id sensor_001 --start-time 1h
```

#### Interactive mode:
```bash
python -m cli.cli interactive
```

#### View trust and traceability information:
```bash
# Query with trust indicators
python -m cli.cli query-data --profile-id <profile_id> --show-trust

# View access logs
python -m cli.cli view-access-logs --limit 50

# Filter logs by consumer
python -m cli.cli view-access-logs --consumer-id cli_user_001
```

#### Search data:
```bash
# Full-text search across all data
python -m cli.cli search-data "temperature"

# Case-sensitive search
python -m cli.cli search-data "Temperature" --case-sensitive

# Search schemas by field name
python -m cli.cli search-schemas "temperature"
```

### Using the Web Interface

The web interface provides a modern, user-friendly way to interact with the system.

#### Access the Interface:
```bash
# Start the web interface (if not already running)
docker-compose up -d web_interface

# Access in browser
open http://localhost:3000
```

#### Features:
- **Dashboard**: View system overview with trust statistics
- **Data Explorer**: Browse sensor data by profile with trust indicators
- **Traceability**: View complete access logs and audit trails
- **Schema Browser**: Explore data schemas with expandable details

For detailed web interface documentation, see [web-interface/README.md](web-interface/README.md)

### Running a Custom Sensor

Create a Python script:

```python
from sensor.sensor import Sensor
import time

# Initialize sensor
sensor = Sensor(
    sensor_id="my_sensor_001",
    device_type="sensor",
    manufacturer="MyCompany",
    model="Model-X",
    certificate="VALID_CERTIFICATE_XYZ"
)

# Connect to gateway
sensor.connect()
time.sleep(3)  # Wait for profile

# Send custom data
sensor.send_data({
    "temperature": 25.5,
    "humidity": 60.0,
    "pressure": 1013.25
})

# Disconnect
sensor.disconnect()
```

## API Documentation

### Consumer Gateway REST API

Base URL: `http://localhost:5000/api`

#### Endpoints

##### 1. Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "service": "Consumer Gateway"
}
```

##### 2. Get All Schemas
```
GET /api/schemas
```
Response:
```json
{
  "success": true,
  "count": 2,
  "schemas": [...]
}
```

##### 3. Get Schema by Profile
```
GET /api/schemas/{profile_id}
```
Response:
```json
{
  "success": true,
  "schema": {
    "profile_id": "abc123",
    "schema": {...},
    "created_at": "2024-01-01T00:00:00",
    "sample_data": {...}
  }
}
```

##### 4. Get Data by Profile
```
GET /api/data/profile/{profile_id}?start_time=2024-01-01T00:00:00&end_time=2024-01-02T00:00:00&limit=100
```
Query Parameters:
- `start_time` (optional): Start timestamp (ISO format)
- `end_time` (optional): End timestamp (ISO format)
- `limit` (optional): Maximum records (default: 100)

Response:
```json
{
  "success": true,
  "count": 10,
  "profile_id": "abc123",
  "data": [...]
}
```

##### 5. Get Data by Sensor
```
GET /api/data/sensor/{sensor_id}?start_time=2024-01-01T00:00:00&limit=100
```
Query Parameters: Same as above

##### 6. Get Profile IDs
```
GET /api/profiles
```
Response:
```json
{
  "success": true,
  "count": 2,
  "profile_ids": ["abc123", "def456"]
}
```

##### 7. Get Access Logs (NEW!)
```
GET /api/access-logs?consumer_id=cli_user&limit=50
```
Query Parameters:
- `consumer_id` (optional): Filter by consumer ID
- `resource_id` (optional): Filter by resource ID
- `limit` (optional): Maximum records (default: 100)

Response:
```json
{
  "success": true,
  "count": 25,
  "logs": [
    {
      "consumer_id": "cli_user_001",
      "action": "query_data",
      "resource_type": "profile",
      "resource_id": "abc123",
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

##### 8. Search Data (NEW!)
```
GET /api/search?query=temperature&case_sensitive=false&limit=50
```
Query Parameters:
- `query` (required): Search string
- `case_sensitive` (optional): Case-sensitive search (default: false)
- `limit` (optional): Maximum records (default: 100)

Response:
```json
{
  "success": true,
  "count": 15,
  "data": [...]
}
```

**Note**: All data query endpoints now include trust and traceability information:
```json
{
  "trust_info": {
    "trusted_records": 95,
    "signed_records": 98,
    "trust_percentage": 95.0
  },
  "traceability": {
    "consumer_id": "cli_user_001",
    "access_logged": true
  }
}
```

## Development

### Project Structure

```
iot-data-lake-system/
├── config/                 # Configuration files
│   ├── config.py          # System configuration
│   └── mosquitto.conf     # MQTT broker config
├── gateway/               # Gateway module
│   ├── gateway.py         # Main gateway logic
│   └── encryption.py      # AES encryption utilities
├── sensor/                # Sensor module
│   └── sensor.py          # Sensor implementation
├── data_lake/             # Data Lake module
│   └── data_lake.py       # MongoDB interface
├── consumer_gateway/      # Consumer Gateway API
│   └── consumer_gateway.py # Flask REST API
├── cli/                   # CLI module
│   └── cli.py             # Command-line interface
├── profile_store/         # Profile Store (black box)
│   └── profile_store.py   # Profile generation
├── tests/                 # Test files
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile.*           # Docker build files
├── requirements.txt       # Python dependencies
├── run_gateway.py         # Gateway runner script
├── run_sensor.py          # Sensor runner script
└── README.md              # This file
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

### Adding a New Sensor Type

1. Create sensor instance with appropriate device_type:
```python
sensor = Sensor(
    sensor_id="camera_001",
    device_type="camera",  # Change device type
    manufacturer="CamCorp",
    model="HD-200",
    certificate="VALID_CERT"
)
```

2. The Profile Store will automatically generate appropriate profile based on device type.

## Troubleshooting

### Common Issues

#### 1. MQTT Connection Failed
```bash
# Check if Mosquitto is running
docker-compose ps mosquitto
# Or for manual installation
sudo systemctl status mosquitto

# Check logs
docker-compose logs mosquitto
```

#### 2. MongoDB Connection Failed
```bash
# Check if MongoDB is running
docker-compose ps mongodb
# Or for manual installation
sudo systemctl status mongodb

# Check logs
docker-compose logs mongodb
```

#### 3. Consumer Gateway Not Responding
```bash
# Check if service is running
docker-compose ps consumer_gateway

# Check logs
docker-compose logs consumer_gateway

# Test health endpoint
curl http://localhost:5000/health
```

#### 4. Sensor Not Connecting
- Verify MQTT broker is accessible
- Check sensor logs for authentication errors
- Ensure certificate is valid
- Verify encryption key matches between sensor and gateway

#### 5. No Data in CLI
- Ensure sensor has sent data
- Check Gateway logs for data reception
- Verify Data Lake connection
- Check MongoDB for stored data:
```bash
docker-compose exec mongodb mongosh
use iot_data_lake
db.sensor_data.find().limit(5)
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f consumer_gateway
docker-compose logs -f sensor_simulator
```

## Security Considerations

1. **Change Default Encryption Key**: Update `AES_KEY` in `.env`
2. **Use Strong Certificates**: Replace mock certificates with real ones
3. **Enable MQTT Authentication**: Configure Mosquitto with username/password
4. **Use TLS/SSL**: Enable encrypted MQTT connections
5. **Secure API**: Add authentication to Consumer Gateway API
6. **Network Isolation**: Use Docker networks to isolate services

## Performance Tuning

1. **MongoDB Indexing**: Indexes are automatically created on `sensor_id`, `profile_id`, and `timestamp`
2. **MQTT QoS**: Adjust Quality of Service levels based on requirements
3. **Data Retention**: Implement TTL indexes for automatic data cleanup
4. **Batch Processing**: Modify Gateway to batch data inserts

## License

[Your License Here]

## Contributing

[Contributing Guidelines]

## Support

For issues and questions:
- GitHub Issues: [Your Repository]
- Email: [Your Email]
- Documentation: [Your Docs URL]