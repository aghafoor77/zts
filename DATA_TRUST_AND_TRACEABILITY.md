# Data Trust and Traceability System

This document explains how the IoT system ensures **data trust** and provides **complete traceability** from data generation to consumption.

---

## 🔐 Data Trust Mechanisms

### Overview
Data trust ensures that consumers can verify the authenticity and integrity of sensor data. The system implements **digital signatures** on sensor data to provide cryptographic proof of data origin and integrity.

### How It Works

#### 1. Data Signing (Sensor Side)
When a sensor with certificate-based authentication sends data, it:

1. **Prepares data with metadata**:
```python
data_with_metadata = {
    'sensor_id': 'sensor_001',
    'profile_id': 'profile_123',
    'timestamp': '2026-06-11T12:00:00Z',
    'data': {'temperature': 25.5, 'humidity': 55.0},
    'data_owner': 'TempCorp_TH-100_sensor_001'
}
```

2. **Signs the data** using its private key:
```python
data_json = json.dumps(data_with_metadata)
signature = sign_with_private_key(data_json, private_key)
```

3. **Sends signed data**:
```python
payload = {
    'sensor_id': 'sensor_001',
    'data': encrypted_data,
    'data_signature': signature_base64,
    'signed': True
}
```

#### 2. Signature Verification (Gateway Side)
The Gateway verifies data signatures:

1. **Extracts sensor's certificate** from profile
2. **Loads public key** from certificate
3. **Verifies signature** using RSA-PSS with SHA-256
4. **Marks data as trusted** if verification succeeds

```python
# Gateway verification
public_key = cert.public_key()
public_key.verify(signature, data_bytes, padding.PSS(...), hashes.SHA256())
# If successful: data_trusted = True
```

#### 3. Trust Indicators in Data Lake
Each data record includes trust metadata:

```json
{
  "sensor_id": "sensor_001",
  "profile_id": "profile_123",
  "timestamp": "2026-06-11T12:00:00Z",
  "data_trusted": true,        // ✓ Signature verified
  "data_signed": true,          // Data was signed
  "data_owner": "TempCorp_TH-100_sensor_001",
  "gateway_received_at": "2026-06-11T12:00:01Z",
  "data": {...}
}
```

### Trust Levels

| Trust Level | Description | Indicator |
|-------------|-------------|-----------|
| **Trusted** | Data signed and signature verified | `data_trusted: true` |
| **Signed but Unverified** | Data signed but verification failed | `data_signed: true, data_trusted: false` |
| **Unsigned** | Data not signed (username/password auth) | `data_signed: false` |

### Consumer View of Trust

When consumers query data, they receive trust statistics:

```json
{
  "success": true,
  "count": 100,
  "trust_info": {
    "trusted_records": 95,
    "signed_records": 95,
    "trust_percentage": 95.0
  },
  "data": [...]
}
```

---

## 📊 Traceability System

### Overview
Traceability tracks the complete lifecycle of data from generation to consumption, answering:
- **Who** owns the data?
- **Who** is accessing the data?
- **When** was the data accessed?
- **What** actions were performed?

### Components

#### 1. Data Ownership Tracking

**At Data Generation:**
```python
data_owner = f"{manufacturer}_{model}_{sensor_id}"
# Example: "TempCorp_TH-100_sensor_001"
```

**Stored in every data record:**
```json
{
  "data_owner": "TempCorp_TH-100_sensor_001",
  "sensor_id": "sensor_001",
  "profile_id": "profile_123"
}
```

#### 2. Access Logging

**Every data access is logged:**
```python
data_lake.log_data_access(
    consumer_id='cli_user_001',
    action='query',
    resource_type='profile',
    resource_id='profile_123',
    metadata={
        'start_time': '2026-06-11T00:00:00Z',
        'end_time': '2026-06-11T12:00:00Z',
        'limit': 100,
        'ip_address': '192.168.1.100'
    }
)
```

**Access log entry:**
```json
{
  "consumer_id": "cli_user_001",
  "action": "query",
  "resource_type": "profile",
  "resource_id": "profile_123",
  "timestamp": "2026-06-11T12:30:00Z",
  "metadata": {
    "start_time": "2026-06-11T00:00:00Z",
    "end_time": "2026-06-11T12:00:00Z",
    "limit": 100,
    "ip_address": "192.168.1.100"
  }
}
```

#### 3. Timestamps

Multiple timestamps track data flow:

```json
{
  "timestamp": "2026-06-11T12:00:00Z",           // Sensor generation time
  "gateway_received_at": "2026-06-11T12:00:01Z", // Gateway receipt time
  "stored_at": "2026-06-11T12:00:02Z"            // Data Lake storage time
}
```

---

## 🔍 Querying with Trust and Traceability

### API Endpoints

#### 1. Query Data with Trust Info
```bash
GET /api/data/profile/{profile_id}?consumer_id=user_001

Response:
{
  "success": true,
  "count": 100,
  "trust_info": {
    "trusted_records": 95,
    "signed_records": 95,
    "trust_percentage": 95.0
  },
  "traceability": {
    "consumer_id": "user_001",
    "access_logged": true
  },
  "data": [...]
}
```

#### 2. View Access Logs
```bash
GET /api/access-logs?consumer_id=user_001&limit=50

Response:
{
  "success": true,
  "count": 50,
  "logs": [
    {
      "consumer_id": "user_001",
      "action": "query",
      "resource_type": "profile",
      "resource_id": "profile_123",
      "timestamp": "2026-06-11T12:30:00Z",
      "metadata": {...}
    },
    ...
  ]
}
```

#### 3. Filter by Trust Level
```bash
# Query only trusted data
GET /api/data/profile/{profile_id}?trusted_only=true
```

---

## 📋 Use Cases

### Use Case 1: Verify Data Authenticity

**Scenario:** Consumer wants to ensure data is authentic

**Solution:**
1. Query data with trust info
2. Check `trust_percentage` in response
3. Filter records where `data_trusted: true`
4. Verify `data_owner` matches expected source

```python
response = requests.get(
    f'/api/data/profile/{profile_id}',
    params={'consumer_id': 'auditor_001'}
)

trust_info = response.json()['trust_info']
if trust_info['trust_percentage'] >= 95:
    print("✓ Data is highly trusted")
else:
    print("⚠ Warning: Low trust percentage")
```

### Use Case 2: Audit Data Access

**Scenario:** Compliance officer needs to audit who accessed sensitive data

**Solution:**
1. Query access logs for specific resource
2. Review consumer IDs and timestamps
3. Analyze access patterns

```python
logs = requests.get(
    '/api/access-logs',
    params={'resource_id': 'profile_sensitive_123'}
).json()['logs']

for log in logs:
    print(f"{log['consumer_id']} accessed data at {log['timestamp']}")
```

### Use Case 3: Track Data Lineage

**Scenario:** Trace data from sensor to consumer

**Solution:**
1. Check `data_owner` field
2. Review timestamps (generation → gateway → storage)
3. Check access logs for consumption history

```json
{
  "data_owner": "TempCorp_TH-100_sensor_001",  // Origin
  "timestamp": "2026-06-11T12:00:00Z",         // Generated
  "gateway_received_at": "2026-06-11T12:00:01Z", // Received
  "accessed_by": ["user_001", "user_002"]       // Consumed
}
```

---

## 🛡️ Security and Privacy

### Data Owner Privacy
- Data owner information is stored but can be anonymized
- Access logs can be encrypted
- PII can be hashed or tokenized

### Access Control
- Consumer IDs can be authenticated
- Role-based access control (RBAC) can be implemented
- Access logs provide audit trail for compliance

### GDPR Compliance
- Data ownership tracking supports data subject rights
- Access logs enable "right to know" compliance
- Data can be deleted with full traceability

---

## 📊 MongoDB Collections

### 1. sensor_data
```javascript
{
  _id: ObjectId,
  sensor_id: "sensor_001",
  profile_id: "profile_123",
  timestamp: ISODate,
  data_trusted: true,           // Trust indicator
  data_signed: true,
  data_owner: "TempCorp_TH-100_sensor_001",  // Ownership
  gateway_received_at: ISODate,
  data: {...}
}

// Indexes
db.sensor_data.createIndex({"data_trusted": 1})
db.sensor_data.createIndex({"data_owner": 1})
```

### 2. access_logs
```javascript
{
  _id: ObjectId,
  consumer_id: "user_001",      // Who accessed
  action: "query",              // What action
  resource_type: "profile",     // What resource type
  resource_id: "profile_123",   // Which resource
  timestamp: ISODate,           // When
  metadata: {                   // Additional context
    ip_address: "192.168.1.100",
    start_time: ISODate,
    end_time: ISODate,
    limit: 100
  }
}

// Indexes
db.access_logs.createIndex({"timestamp": -1})
db.access_logs.createIndex({"consumer_id": 1})
db.access_logs.createIndex({"resource_id": 1})
```

---

## 🔧 Implementation Details

### Sensor-Side Implementation
```python
# In sensor/sensor.py
def send_data(self, data):
    # Add ownership metadata
    data_with_metadata = {
        'sensor_id': self.sensor_id,
        'profile_id': self.profile.get('profileID'),
        'timestamp': datetime.utcnow().isoformat(),
        'data': data,
        'data_owner': f"{self.manufacturer}_{self.model}_{self.sensor_id}"
    }
    
    # Sign if certificate-based auth
    if self.private_key_pem:
        signature = self.sign_data(
            json.dumps(data_with_metadata).encode(),
            self.private_key_pem
        )
    
    # Send with signature
    payload = {
        'sensor_id': self.sensor_id,
        'data': encrypted_data,
        'data_signature': signature,
        'signed': True
    }
```

### Gateway-Side Implementation
```python
# In gateway/gateway.py
def _handle_sensor_data(self, payload):
    # Verify signature if present
    if is_signed and data_signature:
        data_trusted = self._verify_data_signature(
            sensor_data, data_signature, sensor_id
        )
    
    # Add trust and traceability metadata
    data_lake_entry = {
        'sensor_id': sensor_id,
        'profile_id': profile['profileID'],
        'timestamp': datetime.utcnow().isoformat(),
        'data_trusted': data_trusted,
        'data_signed': is_signed,
        'data_owner': sensor_data.get('data_owner'),
        'gateway_received_at': datetime.utcnow().isoformat(),
        'data': sensor_data
    }
```

### Consumer Gateway Implementation
```python
# In consumer_gateway/consumer_gateway.py
@app.route('/api/data/profile/<profile_id>')
def get_data_by_profile(profile_id):
    consumer_id = request.args.get('consumer_id', 'anonymous')
    
    # Log access for traceability
    data_lake.log_data_access(
        consumer_id=consumer_id,
        action='query',
        resource_type='profile',
        resource_id=profile_id,
        metadata={'ip_address': request.remote_addr}
    )
    
    # Return data with trust info
    return {
        'trust_info': {
            'trusted_records': trusted_count,
            'trust_percentage': trust_percentage
        },
        'traceability': {
            'consumer_id': consumer_id,
            'access_logged': True
        },
        'data': data
    }
```

---

## 📈 Benefits

### For Data Producers (Sensors)
- ✓ Proof of data origin
- ✓ Non-repudiation
- ✓ Data integrity protection

### For Data Consumers
- ✓ Verify data authenticity
- ✓ Trust indicators for decision-making
- ✓ Transparency in data quality

### For System Operators
- ✓ Complete audit trail
- ✓ Compliance support (GDPR, HIPAA, etc.)
- ✓ Security incident investigation
- ✓ Usage analytics

### For Regulators/Auditors
- ✓ Full traceability from source to consumption
- ✓ Access logs for compliance verification
- ✓ Data ownership tracking
- ✓ Tamper-evident records

---

## 🚀 Future Enhancements

1. **Blockchain Integration**: Store data hashes on blockchain for immutable audit trail
2. **Zero-Knowledge Proofs**: Verify data properties without revealing data
3. **Differential Privacy**: Add noise while maintaining traceability
4. **Smart Contracts**: Automate access control and payment based on usage
5. **Data Marketplace**: Enable data trading with full traceability

---

**Made with Bob**