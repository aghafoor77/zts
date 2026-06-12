# IoT Sensor Authentication - Dual Mode Support

The IoT system now supports **two authentication methods** that are automatically selected based on the device profile:

1. **Username/Password Authentication** (Traditional)
2. **Certificate-Based Authentication** (PKI/Digital Signature)

## How It Works

### 1. Profile Generation

When a sensor connects, the **ProfileStore** analyzes the certificate format and automatically determines the authentication type:

```python
# In profile_store.py
def _determine_auth_type(self, certificate: str) -> int:
    # If certificate is in PEM format -> CERT_BASED
    if "-----BEGIN CERTIFICATE-----" in certificate:
        return AuthenticationType.CERT_BASED
    else:
        return AuthenticationType.USERNAME_PASSWORD
```

**Profile Fields:**
- `required_authentication`: `0` (USERNAME_PASSWORD) or `3` (CERT_BASED)
- `certificate_hash`: SHA-256 hash of certificate (for CERT_BASED only)

### 2. Sensor Authentication

The sensor reads the profile and automatically uses the appropriate authentication method:

#### Username/Password Authentication
```python
auth_data = {
    'sensor_id': 'sensor_001',
    'auth_type': 'USERNAME_PASSWORD',
    'username': 'sensor_sensor_001',
    'password': 'secure_password'
}
```

#### Certificate-Based Authentication
```python
# Generate random challenge
challenge = secrets.token_bytes(32)  # 256-bit random number

# Sign challenge with private key
signature = sign_with_private_key(challenge, private_key)

auth_data = {
    'sensor_id': 'sensor_001',
    'auth_type': 'CERT_BASED',
    'challenge': challenge.hex(),
    'signature': base64.b64encode(signature),
    'certificate': certificate_pem,
    'timestamp': datetime.utcnow().isoformat(),
    'algorithm': 'RSA-PSS-SHA256'
}
```

### 3. Gateway Verification

The Gateway verifies authentication based on the type:

#### Username/Password Verification
```python
# Simple credential check (mock implementation)
auth_success = username and password
```

#### Certificate-Based Verification
```python
# 1. Load certificate and extract public key
cert = x509.load_pem_x509_certificate(certificate_pem)
public_key = cert.public_key()

# 2. Verify signature
public_key.verify(
    signature,
    challenge_bytes,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256())),
    hashes.SHA256()
)
```

## Configuration

### Sensor Initialization

#### With Username/Password (Simple Certificate)
```python
sensor = Sensor(
    sensor_id="sensor_001",
    device_type="sensor",
    manufacturer="TempCorp",
    model="TH-100",
    certificate="SIMPLE_CERT_12345"  # Not PEM format
)
```
**Result:** Profile will have `required_authentication = 0` (USERNAME_PASSWORD)

#### With Certificate-Based (PEM Certificate)
```python
from config.sensor_credentials import SENSOR_CERTIFICATE_PEM, SENSOR_PRIVATE_KEY_PEM

sensor = Sensor(
    sensor_id="sensor_001",
    device_type="sensor",
    manufacturer="TempCorp",
    model="TH-100",
    certificate=SENSOR_CERTIFICATE_PEM,  # PEM format
    private_key_pem=SENSOR_PRIVATE_KEY_PEM  # Required for signing
)
```
**Result:** Profile will have `required_authentication = 3` (CERT_BASED)

## Authentication Flow

### Username/Password Flow

```
Sensor                    Gateway
  |                          |
  |---(1) Connect Request--->|
  |<--(2) Profile (auth=0)---|
  |                          |
  |---(3) Username/Password->|
  |                          |
  |      (Gateway verifies)  |
  |                          |
  |<--(4) Auth Response------|
  |    (authenticated=true)  |
  |                          |
  |---(5) Send Data--------->|
```

### Certificate-Based Flow

```
Sensor                    Gateway
  |                          |
  |---(1) Connect Request--->|
  |    (with PEM cert)       |
  |                          |
  |<--(2) Profile (auth=3)---|
  |                          |
  |  (Generate challenge)    |
  |  (Sign with private key) |
  |                          |
  |---(3) Challenge+Signature->|
  |    + Certificate         |
  |                          |
  |      (Gateway verifies   |
  |       signature with     |
  |       cert's public key) |
  |                          |
  |<--(4) Auth Response------|
  |    (authenticated=true)  |
  |                          |
  |---(5) Send Data--------->|
```

## Security Features

### Certificate-Based Authentication Advantages

1. **No Password Transmission**: Private key never leaves the device
2. **Challenge-Response**: Each authentication uses a unique random challenge
3. **Digital Signatures**: Cryptographically verifiable proof of identity
4. **PKI Support**: Can integrate with Certificate Authorities (CA)
5. **Non-Repudiation**: Signed challenges provide audit trail

### Implementation Details

**Signature Algorithm:** RSA-PSS with SHA-256
- **Key Size:** 2048-bit RSA
- **Padding:** PSS (Probabilistic Signature Scheme)
- **Hash:** SHA-256
- **Challenge Size:** 256 bits (32 bytes)

## Code Examples

### Example 1: Sensor with Username/Password

```python
# run_sensor.py
sensor = Sensor(
    sensor_id="sensor_001",
    device_type="sensor",
    manufacturer="BasicCorp",
    model="B-100",
    certificate="BASIC_CERT_001"
)

sensor.connect()
# Profile received: required_authentication = 0
# Sensor sends: username + password
# Gateway verifies credentials
# Authentication successful
```

### Example 2: Sensor with Certificate

```python
# run_sensor.py
from config.sensor_credentials import SENSOR_CERTIFICATE_PEM, SENSOR_PRIVATE_KEY_PEM

sensor = Sensor(
    sensor_id="sensor_001",
    device_type="sensor",
    manufacturer="SecureCorp",
    model="S-200",
    certificate=SENSOR_CERTIFICATE_PEM,
    private_key_pem=SENSOR_PRIVATE_KEY_PEM
)

sensor.connect()
# Profile received: required_authentication = 3
# Sensor generates challenge: 32 random bytes
# Sensor signs challenge with private key
# Sensor sends: challenge + signature + certificate
# Gateway verifies signature with certificate's public key
# Authentication successful
```

## Environment Variables

You can override authentication credentials via environment variables:

```bash
# For username/password
export SENSOR_ID="sensor_001"
export USERNAME="sensor_001"
export PASSWORD="secure_password"

# For certificate-based
export CERTIFICATE="$(cat certs/sensor_001_cert.pem)"
export PRIVATE_KEY="$(cat certs/sensor_001_key.pem)"
```

## Logs and Monitoring

### Sensor Logs

**Username/Password:**
```
INFO - Sensor sensor_001 sent username/password authentication request
INFO - Sensor sensor_001 authenticated successfully
```

**Certificate-Based:**
```
INFO - Challenge generated and signed: 918142a6153cffa5...
INFO - Sensor sensor_001 sent certificate-based authentication request
INFO - Sensor sensor_001 authenticated successfully
```

### Gateway Logs

**Username/Password:**
```
INFO - Authentication request from sensor sensor_001 (type: USERNAME_PASSWORD)
INFO - Authentication response sent to sensor sensor_001: True (USERNAME_PASSWORD)
```

**Certificate-Based:**
```
INFO - Authentication request from sensor sensor_001 (type: CERT_BASED)
INFO - Certificate-based authentication successful for sensor sensor_001
INFO - Authentication response sent to sensor sensor_001: True (CERT_BASED)
```

## Testing

### Test Username/Password Authentication

```bash
# Use simple certificate (not PEM)
python run_sensor.py
# Check logs for "USERNAME_PASSWORD" authentication
```

### Test Certificate-Based Authentication

```bash
# Use PEM certificate with private key
export CERTIFICATE="$(cat certs/sensor_001_cert.pem)"
export PRIVATE_KEY="$(cat certs/sensor_001_key.pem)"
python run_sensor.py
# Check logs for "CERT_BASED" authentication
```

## Migration Guide

### Upgrading from Username/Password to Certificate-Based

1. **Generate Certificate:**
   ```bash
   python generate_certificate.py
   ```

2. **Update Sensor Configuration:**
   ```python
   # Before
   sensor = Sensor(..., certificate="SIMPLE_CERT")
   
   # After
   from config.sensor_credentials import SENSOR_CERTIFICATE_PEM, SENSOR_PRIVATE_KEY_PEM
   sensor = Sensor(..., 
                   certificate=SENSOR_CERTIFICATE_PEM,
                   private_key_pem=SENSOR_PRIVATE_KEY_PEM)
   ```

3. **Restart Sensor:**
   ```bash
   docker-compose restart iot_sensor_simulator
   ```

4. **Verify:**
   ```bash
   docker-compose logs iot_sensor_simulator | grep "CERT_BASED"
   ```

## Troubleshooting

### Issue: "Certificate-based auth required but no private key provided"
**Solution:** Ensure `private_key_pem` parameter is provided when initializing the sensor.

### Issue: "Certificate-based authentication failed"
**Possible Causes:**
- Invalid certificate format
- Signature verification failed
- Certificate expired
- Private key doesn't match certificate

**Solution:** Regenerate certificate and private key using `generate_certificate.py`.

### Issue: Profile shows wrong authentication type
**Solution:** Check certificate format. PEM certificates must include:
```
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
```

## Best Practices

1. **Use Certificate-Based for Production**: More secure than username/password
2. **Rotate Certificates Regularly**: Generate new certificates before expiration
3. **Secure Private Keys**: Never commit private keys to version control
4. **Use Hardware Security Modules (HSM)**: For production deployments
5. **Implement Certificate Revocation**: Use CRL or OCSP for revoked certificates
6. **Monitor Authentication Failures**: Set up alerts for failed authentications

---

**Made with Bob**