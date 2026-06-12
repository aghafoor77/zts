"""
Sensor Module - MQTT Client with Encryption and Authentication
Simulates IoT sensors that connect to the Gateway
"""
import json
import logging
import time
import os
import secrets
import base64
import paho.mqtt.client as mqtt
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from gateway.encryption import AESEncryption
from config.config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE,
    MQTT_TOPIC_CONNECT, MQTT_TOPIC_PROFILE, MQTT_TOPIC_DATA,
    MQTT_TOPIC_AUTH, AES_KEY, BinaryFlag, AuthenticationType
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Sensor:
    """
    IoT Sensor that connects to Gateway via MQTT
    """
    
    def __init__(self, sensor_id: str, device_type: str, manufacturer: str,
                 model: str, certificate: str, private_key_pem: str = None):
        """
        Initialize the Sensor
        
        Args:
            sensor_id: Unique sensor identifier
            device_type: Type of device (sensor, camera, etc.)
            manufacturer: Device manufacturer
            model: Device model
            certificate: Device certificate for authentication
            private_key_pem: Private key in PEM format (for certificate-based auth)
        """
        self.sensor_id = sensor_id
        self.device_type = device_type
        self.manufacturer = manufacturer
        self.model = model
        self.certificate = certificate
        self.private_key_pem = private_key_pem
        
        self.profile: Optional[Dict[str, Any]] = None
        self.authenticated = False
        self.encryption = AESEncryption(AES_KEY)
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=sensor_id, protocol=mqtt.MQTTv311)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        logger.info(f"Sensor {sensor_id} initialized")
        
    @staticmethod
    def load_certificate_from_pem(pem_data: str) -> x509.Certificate:
        """
        Load X.509 certificate from PEM format string
        
        Args:
            pem_data: Certificate in PEM format
            
        Returns:
            x509.Certificate object
        """
        try:
            cert = x509.load_pem_x509_certificate(
                pem_data.encode('utf-8'),
                default_backend()
            )
            logger.info(f"Certificate loaded: Subject={cert.subject}, Valid until={cert.not_valid_after}")
            return cert
        except Exception as e:
            logger.error(f"Failed to load certificate: {e}")
            raise
    
    @staticmethod
    def load_private_key_from_pem(pem_data: str):
        """
        Load RSA private key from PEM format string
        
        Args:
            pem_data: Private key in PEM format
            
        Returns:
            RSA private key object
        """
        try:
            private_key = serialization.load_pem_private_key(
                pem_data.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            logger.info(f"Private key loaded: Key size={private_key.key_size} bits")
            return private_key
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise
    
    def sign_data(self, data: bytes, private_key_pem: str) -> str:
        """
        Digitally sign data using RSA private key with SHA-256
        
        Args:
            data: Data to sign (bytes)
            private_key_pem: Private key in PEM format
            
        Returns:
            Base64-encoded signature string
        """
        try:
            # Load private key
            private_key = self.load_private_key_from_pem(private_key_pem)
            
            # Sign the data using RSA-PSS with SHA-256
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature as base64 for transmission
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            logger.info(f"Data signed successfully (signature length: {len(signature)} bytes)")
            return signature_b64
            
        except Exception as e:
            logger.error(f"Failed to sign data: {e}")
            raise
    
    def verify_signature(self, data: bytes, signature_b64: str, certificate_pem: str) -> bool:
        """
        Verify digital signature using certificate's public key
        
        Args:
            data: Original data (bytes)
            signature_b64: Base64-encoded signature
            certificate_pem: Certificate in PEM format
            
        Returns:
            bool: True if signature is valid
        """
        try:
            # Load certificate and extract public key
            cert = self.load_certificate_from_pem(certificate_pem)
            public_key = cert.public_key()
            
            # Decode signature from base64
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.info("Signature verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def generate_and_sign_challenge(self, private_key_pem: str) -> Dict[str, str]:
        """
        Generate a random challenge number and sign it
        
        Args:
            private_key_pem: Private key in PEM format
            
        Returns:
            Dictionary containing challenge, signature, and timestamp
        """
        try:
            # Generate random challenge (32 bytes = 256 bits)
            challenge = secrets.token_bytes(32)
            challenge_hex = challenge.hex()
            
            # Sign the challenge
            signature = self.sign_data(challenge, private_key_pem)
            
            # Create response
            response = {
                'sensor_id': self.sensor_id,
                'challenge': challenge_hex,
                'signature': signature,
                'timestamp': datetime.utcnow().isoformat(),
                'algorithm': 'RSA-PSS-SHA256'
            }
            
            logger.info(f"Challenge generated and signed: {challenge_hex[:16]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate and sign challenge: {e}")
            raise

        logger.info(f"Sensor {sensor_id} initialized")
    
    def connect(self):
        """Connect to the Gateway"""
        try:
            self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
            self.client.loop_start()
            logger.info(f"Sensor {self.sensor_id} connecting to Gateway")
        except Exception as e:
            logger.error(f"Failed to connect sensor {self.sensor_id}: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from the Gateway"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info(f"Sensor {self.sensor_id} disconnected")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info(f"Sensor {self.sensor_id} connected to MQTT broker")
            
            # Subscribe to profile topic
            profile_topic = f"{MQTT_TOPIC_PROFILE}/{self.sensor_id}"
            client.subscribe(profile_topic)
            
            # Subscribe to auth response topic
            auth_topic = f"{MQTT_TOPIC_AUTH}/response/{self.sensor_id}"
            client.subscribe(auth_topic)
            
            # Send connection request
            self._send_connection_request()
        else:
            logger.error(f"Sensor {self.sensor_id} failed to connect, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        try:
            if f"{MQTT_TOPIC_PROFILE}/{self.sensor_id}" in topic:
                self._handle_profile_response(payload)
            elif f"{MQTT_TOPIC_AUTH}/response/{self.sensor_id}" in topic:
                self._handle_auth_response(payload)
        except Exception as e:
            logger.error(f"Error handling message on topic '{topic}': {e}")
    
    def _send_connection_request(self):
        """Send connection request to Gateway"""
        connection_data = {
            'sensor_id': self.sensor_id,
            'device_type': self.device_type,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'certificate': self.certificate
        }
        
        self.client.publish(MQTT_TOPIC_CONNECT, json.dumps(connection_data))
        logger.info(f"Sensor {self.sensor_id} sent connection request")
    
    def _handle_profile_response(self, payload: str):
        """
        Handle profile response from Gateway
        
        Args:
            payload: JSON string containing the profile
        """
        try:
            self.profile = json.loads(payload)
            profile_id = self.profile.get('profileID')
            
            logger.info(f"Sensor {self.sensor_id} received profile: {profile_id}")
            logger.info("=================================================")
            logger.info(self.profile)
            # Store profile locally (simulated)
            self._store_profile_locally()
            
            # Perform authentication if required
            if self.profile.get('supports_authentication') == BinaryFlag.YES:
                self._authenticate()
            else:
                self.authenticated = True
                logger.info(f"Sensor {self.sensor_id} ready to send data (no auth required)")
                
        except Exception as e:
            logger.error(f"Error handling profile response: {e}")
    
    def _store_profile_locally(self):
        """Store profile locally (simulated)"""
        # In a real implementation, this would save to local storage
        logger.info(f"Sensor {self.sensor_id} stored profile locally: {self.profile.get('profileID')}")
    
    def _authenticate(self):
        """Perform authentication with Gateway based on profile's authentication type"""
        auth_type = self.profile.get('required_authentication', AuthenticationType.USERNAME_PASSWORD)
        
        if auth_type == AuthenticationType.CERT_BASED:
            # Certificate-based authentication
            if not self.private_key_pem:
                logger.error(f"Sensor {self.sensor_id}: Certificate-based auth required but no private key provided")
                return
            
            # Generate and sign challenge
            challenge_response = self.generate_and_sign_challenge(self.private_key_pem)
            auth_data = {
                'sensor_id': self.sensor_id,
                'auth_type': 'CERT_BASED',
                'challenge': challenge_response['challenge'],
                'signature': challenge_response['signature'],
                'certificate': self.certificate,
                'timestamp': challenge_response['timestamp'],
                'algorithm': challenge_response['algorithm']
            }
            logger.info(f"Sensor {self.sensor_id} sent certificate-based authentication request")
        else:
            # Username/Password authentication
            auth_data = {
                'sensor_id': self.sensor_id,
                'auth_type': 'USERNAME_PASSWORD',
                'username': f"sensor_{self.sensor_id}",
                'password': "secure_password"  # In real implementation, use secure credentials
            }
            logger.info(f"Sensor {self.sensor_id} sent username/password authentication request")
        
        self.client.publish(MQTT_TOPIC_AUTH, json.dumps(auth_data))
    
    def _handle_auth_response(self, payload: str):
        """
        Handle authentication response from Gateway
        
        Args:
            payload: JSON string containing authentication result
        """
        try:
            response = json.loads(payload)
            self.authenticated = response.get('authenticated', False)
            
            if self.authenticated:
                logger.info(f"Sensor {self.sensor_id} authenticated successfully")
            else:
                logger.error(f"Sensor {self.sensor_id} authentication failed")
                
        except Exception as e:
            logger.error(f"Error handling auth response: {e}")
    
    def send_data(self, data: Dict[str, Any]):
        """
        Send sensor data to Gateway with optional digital signature for data trust
        
        Args:
            data: Sensor data dictionary
        """
        if not self.profile:
            logger.warning(f"Sensor {self.sensor_id} has no profile, cannot send data")
            return
        
        if not self.authenticated:
            logger.warning(f"Sensor {self.sensor_id} not authenticated, cannot send data")
            return
        
        try:
            # Add metadata for traceability
            data_with_metadata = {
                'sensor_id': self.sensor_id,
                'profile_id': self.profile.get('profileID'),
                'timestamp': datetime.utcnow().isoformat(),
                'data': data,
                'data_owner': f"{self.manufacturer}_{self.model}_{self.sensor_id}"
            }
            
            # Convert data to JSON
            data_json = json.dumps(data_with_metadata)
            
            # Sign data if certificate-based auth is used (for data trust)
            data_signature = None
            if (self.profile.get('required_authentication') == AuthenticationType.CERT_BASED
                and self.private_key_pem):
                data_signature = self.sign_data(data_json.encode('utf-8'), self.private_key_pem)
                logger.info(f"Sensor {self.sensor_id} signed data for integrity verification")
            
            # Encrypt data if encryption is enabled
            if self.profile.get('supports_encryption') == BinaryFlag.YES:
                encrypted_data = self.encryption.encrypt(data_json)
            else:
                encrypted_data = data_json
            
            # Prepare payload with signature for data trust
            payload = {
                'sensor_id': self.sensor_id,
                'data': encrypted_data,
                'data_signature': data_signature,  # For data integrity verification
                'signed': data_signature is not None
            }
            
            # Send to Gateway
            self.client.publish(MQTT_TOPIC_DATA, json.dumps(payload))
            logger.info(f"Sensor {self.sensor_id} sent data (signed: {data_signature is not None})")
            
        except Exception as e:
            logger.error(f"Error sending data from sensor {self.sensor_id}: {e}")
    
    def start_sending_data(self, data_generator, interval: int = 5):
        """
        Start sending data periodically
        
        Args:
            data_generator: Function that generates sensor data
            interval: Interval in seconds between data transmissions
        """
        logger.info(f"Sensor {self.sensor_id} starting data transmission (interval: {interval}s)")
        
        try:
            while True:
                if self.authenticated and self.profile:
                    data = data_generator()
                    self.send_data(data)
                else:
                    logger.debug(f"Sensor {self.sensor_id} waiting for authentication...")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"Sensor {self.sensor_id} stopping data transmission")


def generate_temperature_data() -> Dict[str, Any]:
    """Generate sample temperature sensor data"""
    import random
    return {
        'temperature': round(random.uniform(20.0, 30.0), 2),
        'humidity': round(random.uniform(40.0, 60.0), 2),
        'timestamp': datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Test the Sensor with self-signed certificate
    certificate_pem = """-----BEGIN CERTIFICATE-----
MIID1jCCAr6gAwIBAgIUYW3w8egt8leUvsFPv3egVcpLowAwDQYJKoZIhvcNAQEL
BQAwgYUxCzAJBgNVBAYTAlNFMRIwEAYDVQQIDAlTdG9ja2hvbG0xEjAQBgNVBAcM
CVN0b2NraG9sbTEYMBYGA1UECgwPSW9UIFNlbnNvcnMgSW5jMRQwEgYDVQQLDAtJ
b1QgRGV2aWNlczEeMBwGA1UEAwwVaW90LXNlbnNvci1zZW5zb3JfMDAxMB4XDTI2
MDYxMTEwNTA0NFoXDTI3MDYxMTEwNTA0NFowgYUxCzAJBgNVBAYTAlNFMRIwEAYD
VQQIDAlTdG9ja2hvbG0xEjAQBgNVBAcMCVN0b2NraG9sbTEYMBYGA1UECgwPSW9U
IFNlbnNvcnMgSW5jMRQwEgYDVQQLDAtJb1QgRGV2aWNlczEeMBwGA1UEAwwVaW90
LXNlbnNvci1zZW5zb3JfMDAxMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC
AQEAuC7YS+t3RtN6PHrgoLEyrDuPrVU+pHV660zh1eij/CLwFf+7hKgQKsPVE5pU
WGTA9alKRoYwpntakjK396BiEnzAy0Mo6yUU7pVgwbMZx/djtHLH8cocOunPUjk4
IqaGai2Rfwf2XvFJEysnAYuXUe0dWgx7gqwwPfiY7lUSt/dgqKNdAUUsZ0bSMjWo
bOu27pWfJETLS4nMRQTWtt+ZOyPwiXxsvYB1rj71zC4N2VYjKcWj1vgUw0x+VK+w
Qr1UAqJLxp2EjhqLBIlSN0vlML7plfYfPlREfzyCC1v233CoRvbP94jK7GHwngLb
Auqcwoo1lfxOl5hcTceUaamIaQIDAQABozwwOjA4BgNVHREEMTAvghdzZW5zb3It
c2Vuc29yXzAwMS5sb2NhbIIUc2Vuc29yXzAwMS5pb3QubG9jYWwwDQYJKoZIhvcN
AQELBQADggEBAI2gDuqWeMVRyylJUyDENRfGRyIP4OWET09on4URmYHCTU0D/Nyj
t2sQrN58iF6nD111pqjzkKAsXQt9R//ZvZyA6InIodRaZ323F/VMb3x7XrugtPiG
YILFUKLvveTryI4i1SbpTMyn75fW78wvZTTVNyarqASDDZPUPbUuE9gSjSBCbyZp
K7ySQypoS9kkg1tuhmXvVDH2l4jqQ7dOWdsJcyypJI1lyi67ThWwMtW7cdGvhAjw
YtRoNN+lLVczmVDF6y4sta1mkSqxkiIut9o/q69K5gbcL3/J9uEuKr7epTRbTDNc
DdvsAdfFGmHMcMRXoOj5tjDm0RAmpCym+t4=
-----END CERTIFICATE-----"""
    
    sensor = Sensor(
        sensor_id="sensor_001",
        device_type="sensor",
        manufacturer="TempCorp",
        model="TH-100",
        certificate=certificate_pem
    )
    
    sensor.connect()
    
    # Wait for profile and authentication
    time.sleep(3)
    
    # Start sending data
    try:
        sensor.start_sending_data(generate_temperature_data, interval=5)
    except KeyboardInterrupt:
        sensor.disconnect()

# Made with # Com 
