# ZTS Data Lake - Complete Deployment Guide

This guide covers deploying the entire Zero Trust Security Data Lake system including the new web interface.

## 🚀 Quick Start (All Services)

### Start Everything with Docker Compose

```bash
# Start all services (Gateway, Consumer Gateway, MongoDB, Mosquitto, Web Interface)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Access Points

Once all services are running:

- **Web Interface**: http://localhost:3000
- **Consumer Gateway API**: http://localhost:5000/api
- **MQTT Broker**: localhost:1883
- **MongoDB**: localhost:27017

## 📦 Services Overview

### 1. MongoDB (Data Lake)
- **Port**: 27017
- **Purpose**: NoSQL database for sensor data and schemas
- **Health Check**: Automatic ping check every 10s

### 2. Mosquitto (MQTT Broker)
- **Ports**: 1883 (MQTT), 9001 (WebSocket)
- **Purpose**: Message broker for sensor communication
- **Health Check**: Subscription test every 10s

### 3. Gateway
- **Purpose**: Handles sensor connections, profile generation, data encryption
- **Dependencies**: Mosquitto, MongoDB
- **Environment Variables**:
  - `MQTT_BROKER_HOST=mosquitto`
  - `MONGO_HOST=mongodb`
  - `AES_KEY=ThisIsASecretKey`

### 4. Consumer Gateway (API)
- **Port**: 5000
- **Purpose**: REST API for data access
- **Dependencies**: MongoDB
- **Health Check**: HTTP GET /health every 10s
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /api/schemas` - List schemas
  - `GET /api/profiles` - List profiles
  - `GET /api/data/profile/:id` - Query profile data
  - `GET /api/access-logs` - View access logs

### 5. Web Interface (NEW!)
- **Port**: 3000
- **Purpose**: Modern React dashboard for data visualization
- **Dependencies**: Consumer Gateway
- **Features**:
  - Dashboard with trust analytics
  - Data explorer with search
  - Traceability viewer
  - Security analytics
  - Schema browser
- **Health Check**: HTTP GET / every 30s

### 6. Sensor Simulator (Optional)
- **Purpose**: Simulates IoT sensor for testing
- **Dependencies**: Gateway, Mosquitto
- **Environment Variables**:
  - `SENSOR_ID=sensor_001`
  - `MANUFACTURER=TempCorp`
  - `MODEL=TH-100`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB_NAME=iot_data_lake

# MQTT
MQTT_BROKER_HOST=mosquitto
MQTT_BROKER_PORT=1883

# Encryption
AES_KEY=ThisIsASecretKey

# Consumer Gateway
CONSUMER_GATEWAY_HOST=0.0.0.0
CONSUMER_GATEWAY_PORT=5000

# Sensor Configuration
SENSOR_ID=sensor_001
DEVICE_TYPE=sensor
MANUFACTURER=TempCorp
MODEL=TH-100
```

## 📋 Step-by-Step Deployment

### 1. Prerequisites

```bash
# Install Docker and Docker Compose
docker --version
docker-compose --version

# Clone the repository
git clone <repository-url>
cd ZTS
```

### 2. Build and Start Services

```bash
# Build all images
docker-compose build

# Start services in detached mode
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps
```

### 3. Verify Services

```bash
# Check all services are running
docker-compose ps

# Expected output:
# NAME                      STATUS              PORTS
# iot_mongodb               Up (healthy)        27017
# iot_mosquitto             Up (healthy)        1883, 9001
# iot_gateway               Up                  -
# iot_consumer_gateway      Up (healthy)        5000
# iot_web_interface         Up (healthy)        3000
# iot_sensor_simulator      Up                  -
```

### 4. Test the System

#### Test Consumer Gateway API
```bash
# Health check
curl http://localhost:5000/health

# List profiles
curl http://localhost:5000/api/profiles

# List schemas
curl http://localhost:5000/api/schemas
```

#### Test Web Interface
```bash
# Open in browser
open http://localhost:3000

# Or use curl
curl http://localhost:3000
```

### 5. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web_interface
docker-compose logs -f consumer_gateway
docker-compose logs -f gateway
```

## 🔍 Monitoring

### Service Health

```bash
# Check health status
docker-compose ps

# Inspect specific service
docker inspect iot_web_interface
docker inspect iot_consumer_gateway
```

### Resource Usage

```bash
# View resource usage
docker stats

# View specific service
docker stats iot_web_interface
```

## 🛠️ Troubleshooting

### Web Interface Not Loading

```bash
# Check if service is running
docker-compose ps web_interface

# View logs
docker-compose logs web_interface

# Restart service
docker-compose restart web_interface
```

### API Connection Issues

```bash
# Check consumer gateway
docker-compose logs consumer_gateway

# Test API directly
curl http://localhost:5000/health

# Check network connectivity
docker-compose exec web_interface ping consumer_gateway
```

### MongoDB Connection Issues

```bash
# Check MongoDB status
docker-compose ps mongodb

# View MongoDB logs
docker-compose logs mongodb

# Test connection
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### MQTT Connection Issues

```bash
# Check Mosquitto status
docker-compose ps mosquitto

# View logs
docker-compose logs mosquitto

# Test MQTT connection
docker-compose exec mosquitto mosquitto_sub -t test -C 1
```

## 🔄 Updates and Maintenance

### Update Services

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Update Web Interface Only

```bash
# Rebuild web interface
docker-compose build web_interface

# Restart service
docker-compose up -d web_interface
```

### Backup Data

```bash
# Backup MongoDB data
docker-compose exec mongodb mongodump --out=/data/backup

# Copy backup to host
docker cp iot_mongodb:/data/backup ./mongodb_backup
```

### Clean Up

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 🌐 Production Deployment

### Security Considerations

1. **Change Default Credentials**
   ```env
   AES_KEY=<generate-strong-key>
   MONGO_INITDB_ROOT_USERNAME=admin
   MONGO_INITDB_ROOT_PASSWORD=<strong-password>
   ```

2. **Use HTTPS**
   - Add SSL certificates
   - Configure nginx with SSL
   - Update docker-compose ports

3. **Network Security**
   - Use firewall rules
   - Limit exposed ports
   - Use Docker secrets for sensitive data

### Scaling

```bash
# Scale sensor simulators
docker-compose up -d --scale sensor_simulator=5

# Use Docker Swarm for production
docker swarm init
docker stack deploy -c docker-compose.yml zts
```

### Monitoring in Production

```bash
# Add monitoring stack (Prometheus + Grafana)
# See monitoring/docker-compose.monitoring.yml

# View metrics
open http://localhost:9090  # Prometheus
open http://localhost:3001  # Grafana
```

## 📊 Usage Examples

### Using the Web Interface

1. **Open Dashboard**
   ```
   http://localhost:3000/dashboard
   ```
   - View trust analytics
   - Monitor system health
   - See real-time statistics

2. **Explore Data**
   ```
   http://localhost:3000/data-explorer
   ```
   - Search sensor data
   - Filter by profile
   - View trust indicators

3. **View Traceability**
   ```
   http://localhost:3000/traceability
   ```
   - Access logs
   - Consumer activity
   - Audit trail

### Using the CLI

```bash
# Query data with trust info
./run_cli.sh query-data --profile-id <profile_id> --show-trust

# View access logs
./run_cli.sh view-access-logs --limit 50

# Search data
./run_cli.sh search-data --query "temperature"

# Search schemas
./run_cli.sh search-schemas --field humidity
```

### Using the API

```bash
# Query data with trust info
curl "http://localhost:5000/api/data/profile/<profile_id>?consumer_id=my_app"

# View access logs
curl "http://localhost:5000/api/access-logs?limit=50"

# Get schemas
curl "http://localhost:5000/api/schemas"
```

## 🎯 Complete System Test

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be healthy
sleep 30

# 3. Test API
curl http://localhost:5000/health

# 4. Test Web Interface
curl http://localhost:3000

# 5. Check sensor data (wait for sensor to send data)
sleep 60
curl http://localhost:5000/api/profiles

# 6. Query data
PROFILE_ID=$(curl -s http://localhost:5000/api/profiles | jq -r '.profile_ids[0]')
curl "http://localhost:5000/api/data/profile/$PROFILE_ID?limit=10"

# 7. Open web interface in browser
open http://localhost:3000
```

## 📝 Summary

### Ports Used
- **3000**: Web Interface
- **5000**: Consumer Gateway API
- **1883**: MQTT Broker
- **9001**: MQTT WebSocket
- **27017**: MongoDB

### Default Access
- Web UI: http://localhost:3000
- API: http://localhost:5000/api
- Health: http://localhost:5000/health

### Quick Commands
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Restart
docker-compose restart

# Update
docker-compose pull && docker-compose up -d
```

---

**Made with Bob - Zero Trust Security Data Lake**