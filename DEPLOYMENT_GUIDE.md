# ZTS Data Lake - Deployment Guide

Complete guide for deploying the Zero Trust Security IoT Data Lake system with all features including CLI, Web Interface, Trust & Traceability.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

## Quick Start

For the fastest deployment using Docker Compose:

```bash
# Clone repository
git clone <repository-url>
cd iot-data-lake-system

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Access web interface
open http://localhost:3000

# Test CLI
python -m cli.cli health
```

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 10 GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for CLI usage)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Network Requirements
- Port 1883 (MQTT)
- Port 5012 (Consumer Gateway API)
- Port 3000 (Web Interface)
- Port 27017 (MongoDB - internal)
- Port 9001 (MQTT WebSocket - optional)

## Installation Steps

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd iot-data-lake-system
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

**Important**: Change the `AES_KEY` in production!

### Step 3: Generate Certificates (Optional)

For production deployment with real sensors:

```bash
# Generate sensor certificates
python generate_certificate.py

# Certificates will be created in certs/ directory
ls -la certs/
```

### Step 4: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 5: Wait for Services

Services need time to initialize:

```bash
# Check service health
docker-compose ps

# All services should show "healthy" or "running"
```

Expected output:
```
NAME                    STATUS
iot_mongodb             Up (healthy)
iot_mosquitto           Up (healthy)
iot_gateway             Up
iot_consumer_gateway    Up (healthy)
iot_web_interface       Up (healthy)
iot_sensor_simulator    Up
```

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# MQTT Configuration
MQTT_BROKER_HOST=mosquitto
MQTT_BROKER_PORT=1883

# MongoDB Configuration
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB_NAME=iot_data_lake

# Consumer Gateway Configuration
CONSUMER_GATEWAY_HOST=0.0.0.0
CONSUMER_GATEWAY_PORT=5012

# Encryption (CHANGE IN PRODUCTION!)
AES_KEY=YourSecretKey123456
```

### Port Configuration

To change default ports, edit `docker-compose.yml`:

```yaml
services:
  consumer_gateway:
    ports:
      - "8080:5012"  # Change 5012 to 8080
  
  web_interface:
    ports:
      - "8000:80"    # Change 3000 to 8000
```

### Sensor Configuration

Configure sensor simulator in `docker-compose.yml`:

```yaml
sensor_simulator:
  environment:
    - SENSOR_ID=sensor_001
    - DEVICE_TYPE=sensor
    - MANUFACTURER=TempCorp
    - MODEL=TH-100
```

## Verification

### 1. Check Service Health

```bash
# All services
docker-compose ps

# Specific service logs
docker-compose logs gateway
docker-compose logs consumer_gateway
```

### 2. Test API

```bash
# Health check
curl http://localhost:5012/health

# List profiles
curl http://localhost:5012/api/profiles

# Get schemas
curl http://localhost:5012/api/schemas
```

### 3. Test Web Interface

Open browser: http://localhost:3000

You should see:
- Dashboard with trust statistics
- Navigation menu (Dashboard, Data Explorer, Traceability, Schemas)
- Zero Trust Security themed UI

### 4. Test CLI

```bash
# Install CLI dependencies
pip install -r requirements.txt

# Check health
python -m cli.cli health

# List profiles
python -m cli.cli list-profiles

# Query data
python -m cli.cli query-data --profile-id <profile_id> --show-trust
```

### 5. Verify Data Flow

```bash
# Check if sensor is sending data
docker-compose logs sensor_simulator | tail -20

# Check if gateway is receiving data
docker-compose logs gateway | tail -20

# Check MongoDB for data
docker-compose exec mongodb mongosh
> use iot_data_lake
> db.sensor_data.countDocuments()
> db.sensor_data.findOne()
```

## Usage Examples

### Web Interface

1. **View Dashboard**
   - Open http://localhost:3000
   - See trust statistics and system overview

2. **Browse Data**
   - Click "Data Explorer"
   - Select a profile from dropdown
   - View data with trust indicators

3. **Check Traceability**
   - Click "Traceability"
   - View access logs and audit trail

4. **Explore Schemas**
   - Click "Schemas"
   - Expand schema details
   - View sample data

### CLI Usage

```bash
# Show trust information
python -m cli.cli query-data --profile-id <id> --show-trust

# View access logs
python -m cli.cli view-access-logs --limit 50

# Search data
python -m cli.cli search-data "temperature"

# Search schemas
python -m cli.cli search-schemas "humidity"

# Interactive mode
python -m cli.cli interactive
```

### API Usage

```bash
# Get data with trust info
curl "http://localhost:5012/api/data/profile/<profile_id>?limit=10"

# Get access logs
curl "http://localhost:5012/api/access-logs?limit=50"

# Search data
curl "http://localhost:5012/api/search?query=temperature&limit=20"
```

## Troubleshooting

### Issue: Services Not Starting

**Solution**:
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Issue: Web Interface Shows API Error

**Solution**:
```bash
# Check Consumer Gateway is running
docker-compose ps consumer_gateway

# Test API directly
curl http://localhost:5012/health

# Check logs
docker-compose logs consumer_gateway
```

### Issue: No Data in Dashboard

**Solution**:
```bash
# Check if sensor is running
docker-compose ps sensor_simulator

# Check sensor logs
docker-compose logs sensor_simulator

# Manually send test data
docker-compose exec sensor_simulator python -c "
from sensor.sensor import Sensor
import time
s = Sensor('test_001', 'sensor', 'Test', 'Model-1', 'CERT')
s.connect()
time.sleep(3)
s.send_data({'temperature': 25.5, 'humidity': 60})
s.disconnect()
"
```

### Issue: Port Already in Use

**Solution**:
```bash
# Find process using port
lsof -i :3000  # or :5012, :1883, etc.

# Kill process or change port in docker-compose.yml
```

### Issue: MongoDB Connection Failed

**Solution**:
```bash
# Check MongoDB is healthy
docker-compose ps mongodb

# Restart MongoDB
docker-compose restart mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

### Issue: CLI Commands Not Working

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+

# Test with verbose output
python -m cli.cli health --verbose
```

## Production Deployment

### Security Hardening

1. **Change Default Keys**
```bash
# Generate strong AES key
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env
AES_KEY=<generated_key>
```

2. **Enable MQTT Authentication**
```bash
# Edit config/mosquitto.conf
allow_anonymous false
password_file /mosquitto/config/passwd

# Create password file
docker-compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd username
```

3. **Enable TLS/SSL**
```bash
# Generate SSL certificates
openssl req -new -x509 -days 365 -extensions v3_ca -keyout ca.key -out ca.crt

# Update mosquitto.conf
listener 8883
cafile /mosquitto/config/ca.crt
certfile /mosquitto/config/server.crt
keyfile /mosquitto/config/server.key
```

4. **Add API Authentication**
- Implement JWT tokens in Consumer Gateway
- Add authentication middleware
- Update web interface to handle tokens

### Performance Optimization

1. **MongoDB Indexes**
```javascript
// Already created automatically:
db.sensor_data.createIndex({ "sensor_id": 1 })
db.sensor_data.createIndex({ "profile_id": 1 })
db.sensor_data.createIndex({ "timestamp": -1 })
db.sensor_data.createIndex({ "data_trusted": 1 })
```

2. **Data Retention**
```javascript
// Add TTL index for automatic cleanup
db.sensor_data.createIndex(
  { "timestamp": 1 },
  { expireAfterSeconds: 2592000 }  // 30 days
)
```

3. **Resource Limits**
```yaml
# In docker-compose.yml
services:
  mongodb:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Monitoring

1. **Health Checks**
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:5012/health || echo "API DOWN"
curl -f http://localhost:3000/ || echo "WEB DOWN"
EOF

chmod +x monitor.sh

# Add to cron
crontab -e
*/5 * * * * /path/to/monitor.sh
```

2. **Log Aggregation**
```bash
# Export logs to file
docker-compose logs -f > system.log 2>&1 &

# Or use log driver
# In docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Backup Strategy

1. **MongoDB Backup**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T mongodb mongodump \
  --db iot_data_lake \
  --archive=/data/backup_$DATE.archive
EOF

chmod +x backup.sh

# Schedule daily backups
crontab -e
0 2 * * * /path/to/backup.sh
```

2. **Configuration Backup**
```bash
# Backup configuration files
tar -czf config_backup.tar.gz .env config/ certs/
```

### Scaling

1. **Horizontal Scaling**
```yaml
# In docker-compose.yml
services:
  gateway:
    deploy:
      replicas: 3
  
  consumer_gateway:
    deploy:
      replicas: 2
```

2. **Load Balancing**
```bash
# Add nginx load balancer
# See nginx.conf example in documentation
```

## Next Steps

After successful deployment:

1. **Customize Sensors**: Add your real IoT devices
2. **Configure Profiles**: Adjust security profiles for your devices
3. **Set Up Monitoring**: Implement comprehensive monitoring
4. **Enable Backups**: Schedule regular backups
5. **Review Security**: Conduct security audit
6. **Train Users**: Provide training on CLI and Web Interface

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review documentation: README.md, CLI_EXAMPLES.md
- Test API: `curl http://localhost:5012/health`

## Additional Resources

- [README.md](README.md) - System overview
- [CLI_EXAMPLES.md](CLI_EXAMPLES.md) - CLI usage examples
- [DATA_TRUST_AND_TRACEABILITY.md](DATA_TRUST_AND_TRACEABILITY.md) - Trust features
- [web-interface/README.md](web-interface/README.md) - Web interface guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture