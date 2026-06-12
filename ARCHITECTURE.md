# System Architecture Documentation

## Overview

The IoT Data Lake System is a comprehensive solution for managing IoT sensor data with secure communication, automatic schema generation, and flexible data access.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              IoT Data Lake System                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐                                              ┌──────────────┐
│   Sensor 1   │                                              │   Sensor N   │
│              │                                              │              │
│ - Device Info│                                              │ - Device Info│
│ - Certificate│                                              │ - Certificate│
│ - Encryption │                                              │ - Encryption │
└──────┬───────┘                                              └──────┬───────┘
       │                                                             │
       │ MQTT (Port 1883)                                           │
       │ Topics:                                                    │
       │ - sensor/connect                                           │
       │ - sensor/profile/{id}                                      │
       │ - sensor/auth                                              │
       │ - sensor/data                                              │
       │                                                             │
       └─────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   MQTT Broker          │
                    │   (Eclipse Mosquitto)  │
                    │                        │
                    │   Port: 1883           │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      Gateway           │
                    │                        │
                    │  ┌──────────────────┐  │
                    │  │ Profile Store    │  │
                    │  │ (Black Box)      │  │
                    │  │                  │  │
                    │  │ - Verify Cert    │  │
                    │  │ - Generate       │  │
                    │  │   Profile        │  │
                    │  │ - Risk Score     │  │
                    │  └──────────────────┘  │
                    │                        │
                    │  ┌──────────────────┐  │
                    │  │ Encryption       │  │
                    │  │ (AES-128-CBC)    │  │
                    │  └──────────────────┘  │
                    │                        │
                    │  ┌──────────────────┐  │
                    │  │ Authentication   │  │
                    │  │ Handler          │  │
                    │  └──────────────────┘  │
                    └────────────┬───────────┘
                                 │
                                 │ Decrypted Data
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     Data Lake          │
                    │     (MongoDB)          │
                    │                        │
                    │  Collections:          │
                    │  - sensor_data         │
                    │  - schemas             │
                    │                        │
                    │  ┌──────────────────┐  │
                    │  │ Schema Generator │  │
                    │  │ (Genson)         │  │
                    │  └──────────────────┘  │
                    │                        │
                    │  Port: 27017           │
                    └────────────┬───────────┘
                                 │
                                 │ Query Data
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Consumer Gateway      │
                    │  (Flask REST API)      │
                    │                        │
                    │  Endpoints:            │
                    │  - GET /api/schemas    │
                    │  - GET /api/profiles   │
                    │  - GET /api/data/...   │
                    │                        │
                    │  Port: 5000            │
                    └────────────┬───────────┘
                                 │
                                 │ HTTP/REST
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │         CLI            │
                    │                        │
                    │  Commands:             │
                    │  - list-schemas        │
                    │  - query-data          │
                    │  - interactive         │
                    └────────────────────────┘
```

## Component Details

### 1. Sensor Layer

**Responsibilities:**
- Connect to Gateway via MQTT
- Request and receive device profile
- Authenticate with Gateway
- Encrypt sensor data using AES
- Transmit data periodically

**Technologies:**
- Python 3.11
- Paho MQTT Client
- PyCryptodome (AES encryption)

**Data Flow:**
1. Send connection request with device info and certificate
2. Receive profile from Gateway
3. Perform authentication if required
4. Encrypt data payload
5. Send encrypted data to Gateway

### 2. MQTT Broker (Eclipse Mosquitto)

**Responsibilities:**
- Message routing between sensors and Gateway
- Topic-based publish/subscribe
- Connection management

**Configuration:**
- Port: 1883 (MQTT)
- Port: 9001 (WebSocket, optional)
- Anonymous connections allowed (for development)

**Topics:**
- `sensor/connect` - Connection requests
- `sensor/profile/{sensor_id}` - Profile delivery
- `sensor/auth` - Authentication requests
- `sensor/auth/response/{sensor_id}` - Auth responses
- `sensor/data` - Sensor data transmission

### 3. Gateway

**Responsibilities:**
- MQTT message handling
- Profile generation via Profile Store
- Authentication management
- Data decryption
- Data forwarding to Data Lake

**Sub-components:**

#### Profile Store (Black Box)
- Verifies device certificates
- Generates security profiles
- Calculates risk scores
- Stores profile mappings

#### Encryption Handler
- AES-128-CBC encryption/decryption
- Key management
- IV generation

#### Authentication Handler
- Username/password verification
- Session management
- Auth response generation

**Technologies:**
- Python 3.11
- Paho MQTT Client
- PyCryptodome

### 4. Data Lake (MongoDB)

**Responsibilities:**
- Store sensor data in JSON format
- Generate and store JSON schemas
- Index data for efficient querying
- Time-series data management

**Collections:**

#### sensor_data
```json
{
  "_id": ObjectId,
  "sensor_id": "sensor_001",
  "profile_id": "abc123",
  "timestamp": "2024-01-01T00:00:00",
  "data": {
    "temperature": 25.5,
    "humidity": 60.0
  }
}
```

**Indexes:**
- `sensor_id` + `timestamp` (compound, descending)
- `profile_id`

#### schemas
```json
{
  "_id": ObjectId,
  "profile_id": "abc123",
  "schema": { /* JSON Schema */ },
  "created_at": "2024-01-01T00:00:00",
  "sample_data": { /* Sample */ }
}
```

**Indexes:**
- `profile_id` (unique)

**Technologies:**
- MongoDB 7.0
- PyMongo (Python driver)
- Genson (Schema generation)

### 5. Consumer Gateway (REST API)

**Responsibilities:**
- Expose REST API for data access
- Query Data Lake
- Format responses
- Handle time-range queries

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/schemas` | List all schemas |
| GET | `/api/schemas/{profile_id}` | Get specific schema |
| GET | `/api/profiles` | List profile IDs |
| GET | `/api/data/profile/{profile_id}` | Query by profile |
| GET | `/api/data/sensor/{sensor_id}` | Query by sensor |

**Technologies:**
- Python 3.11
- Flask (Web framework)
- Flask-CORS

### 6. CLI (Command Line Interface)

**Responsibilities:**
- User interaction
- API consumption
- Data visualization
- Interactive queries

**Commands:**
- `health` - Check system health
- `list-schemas` - List available schemas
- `show-schema` - Show specific schema
- `list-profiles` - List profile IDs
- `query-data` - Query by profile
- `query-sensor` - Query by sensor
- `interactive` - Interactive mode

**Technologies:**
- Python 3.11
- Click (CLI framework)
- Tabulate (Table formatting)
- Requests (HTTP client)

## Data Flow Sequences

### Sensor Connection Sequence

```
Sensor                Gateway              Profile Store        Data Lake
  │                      │                      │                   │
  │──Connection Request──>│                      │                   │
  │  (device info, cert)  │                      │                   │
  │                      │──Verify & Generate──>│                   │
  │                      │                      │                   │
  │                      │<────Profile──────────│                   │
  │<────Profile──────────│                      │                   │
  │                      │                      │                   │
  │──Auth Request────────>│                      │                   │
  │                      │                      │                   │
  │<────Auth Success─────│                      │                   │
  │                      │                      │                   │
```

### Data Transmission Sequence

```
Sensor                Gateway              Data Lake            Consumer GW
  │                      │                      │                   │
  │──Encrypted Data──────>│                      │                   │
  │                      │                      │                   │
  │                      │──Decrypt─────────────>│                   │
  │                      │                      │                   │
  │                      │                      │──Generate Schema──│
  │                      │                      │  (first time)     │
  │                      │                      │                   │
  │                      │                      │──Store Data───────│
  │                      │                      │                   │
```

### Data Query Sequence

```
CLI                Consumer GW          Data Lake
  │                      │                   │
  │──List Schemas────────>│                   │
  │                      │──Query Schemas────>│
  │                      │<──Schemas─────────│
  │<────Schemas──────────│                   │
  │                      │                   │
  │──Query Data──────────>│                   │
  │  (profile, time)     │──Query Data───────>│
  │                      │<──Data────────────│
  │<────Data─────────────│                   │
  │                      │                   │
```

## Security Architecture

### Encryption

**Algorithm:** AES-128-CBC
**Key Management:** Pre-shared key (configurable)
**IV:** Random, prepended to ciphertext

```
Plaintext → AES Encrypt → IV + Ciphertext → Base64 → Transmitted
```

### Authentication

**Method:** Username/Password (extensible to OAuth, OTP)
**Flow:**
1. Sensor sends credentials
2. Gateway verifies
3. Session established
4. Data transmission allowed

### Certificate Verification

**Purpose:** Device identity verification
**Process:**
1. Sensor provides certificate
2. Profile Store verifies against CA (mock)
3. Profile generated if valid
4. Connection rejected if invalid

## Scalability Considerations

### Horizontal Scaling

**Gateway:**
- Multiple Gateway instances
- Load balancer for MQTT
- Shared Profile Store

**Consumer Gateway:**
- Multiple API instances
- Load balancer (nginx, HAProxy)
- Shared Data Lake

**Data Lake:**
- MongoDB replica set
- Sharding by profile_id or sensor_id
- Read replicas for queries

### Performance Optimization

**Indexing:**
- Compound indexes on frequently queried fields
- TTL indexes for data retention

**Caching:**
- Redis for schema caching
- Profile caching in Gateway

**Batching:**
- Batch data inserts
- Bulk schema generation

## Monitoring and Observability

### Metrics

**Gateway:**
- Messages received/second
- Encryption/decryption time
- Profile generation time
- Error rates

**Data Lake:**
- Write throughput
- Query latency
- Storage usage
- Schema count

**Consumer Gateway:**
- Request rate
- Response time
- Error rate
- Active connections

### Logging

**Levels:**
- DEBUG: Detailed flow
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures

**Centralization:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Loki
- CloudWatch (AWS)

## Deployment Architecture

### Docker Compose (Development)

```
Networks:
  - iot_network (bridge)

Volumes:
  - mongodb_data
  - mosquitto_data
  - mosquitto_logs

Services:
  - mongodb (MongoDB 7.0)
  - mosquitto (Eclipse Mosquitto 2.0)
  - gateway (Custom Python)
  - consumer_gateway (Custom Python)
  - sensor_simulator (Custom Python)
```

### Production Deployment

**Kubernetes:**
- Deployments for each service
- StatefulSet for MongoDB
- Services for internal communication
- Ingress for external access
- ConfigMaps for configuration
- Secrets for sensitive data

**Cloud Services:**
- AWS IoT Core (MQTT)
- DocumentDB (MongoDB-compatible)
- ECS/EKS (Container orchestration)
- API Gateway (REST API)
- Lambda (Serverless functions)

## Future Enhancements

1. **Security:**
   - TLS/SSL for MQTT
   - OAuth 2.0 authentication
   - Certificate-based auth
   - API key management

2. **Features:**
   - Real-time data streaming
   - Data aggregation
   - Alerting system
   - Dashboard UI

3. **Scalability:**
   - Kafka for message queue
   - Time-series database (InfluxDB)
   - Distributed tracing
   - Auto-scaling

4. **Analytics:**
   - Machine learning integration
   - Anomaly detection
   - Predictive maintenance
   - Data visualization