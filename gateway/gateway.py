"""
Gateway Module - MQTT Broker and Profile Management
Handles sensor connections, profile generation, and data reception
"""
import json
import logging
import base64
import paho.mqtt.client as mqtt
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from profile_store.profile_store import ProfileStore
from gateway.encryption import AESEncryption
from config.config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE,
    MQTT_TOPIC_CONNECT, MQTT_TOPIC_PROFILE, MQTT_TOPIC_DATA,
    MQTT_TOPIC_AUTH, AES_KEY, BinaryFlag, AuthenticationType
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Gateway:
    """
    Gateway that handles MQTT connections, profile generation, and data reception
    """
    
    def __init__(self, data_lake_callback=None):
        """
        Initialize the Gateway
        
        Args:
            data_lake_callback: Callback function to send data to Data Lake
        """
        self.profile_store = ProfileStore()
        self.encryption = AESEncryption(AES_KEY)
        self.data_lake_callback = data_lake_callback
        self.connected_sensors = {}  # sensor_id -> profile mapping
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id="gateway", protocol=mqtt.MQTTv311)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        logger.info("Gateway initialized")
    
    def start(self):
        """Start the Gateway MQTT broker"""
        try:
            self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
            self.client.loop_start()
            logger.info(f"Gateway started on {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        except Exception as e:
            logger.error(f"Failed to start Gateway: {e}")
            raise
    
    def stop(self):
        """Stop the Gateway"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Gateway stopped")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Gateway connected to MQTT broker")
            # Subscribe to relevant topics
            client.subscribe(MQTT_TOPIC_CONNECT)
            client.subscribe(MQTT_TOPIC_DATA)
            client.subscribe(MQTT_TOPIC_AUTH)
            logger.info(f"Subscribed to topics: {MQTT_TOPIC_CONNECT}, {MQTT_TOPIC_DATA}, {MQTT_TOPIC_AUTH}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.info(f"Received message on topic '{topic}'")
        
        try:
            if topic == MQTT_TOPIC_CONNECT:
                self._handle_connection_request(payload)
            elif topic == MQTT_TOPIC_AUTH:
                self._handle_authentication(payload)
            elif topic == MQTT_TOPIC_DATA:
                self._handle_sensor_data(payload)
        except Exception as e:
            logger.error(f"Error handling message on topic '{topic}': {e}")
    
    def _handle_connection_request(self, payload: str):
        """
        Handle sensor connection request
        
        Args:
            payload: JSON string containing device info and certificate
        """
        try:
            data = json.loads(payload)
            sensor_id = data.get('sensor_id')
            device_info = {
                'device_type': data.get('device_type'),
                'manufacturer': data.get('manufacturer'),
                'model': data.get('model')
            }
            certificate = data.get('certificate')
            
            logger.info(f"Connection request from sensor {sensor_id}")
            
            # Generate profile using Profile Store
            profile = self.profile_store.generate_profile(device_info, certificate)
            
            # Store certificate in profile for data signature verification
            profile['certificate_pem'] = certificate
            
            # Store sensor connection with certificate
            self.connected_sensors[sensor_id] = profile
            
            # Send profile back to sensor
            profile_topic = f"{MQTT_TOPIC_PROFILE}/{sensor_id}"
            self.client.publish(profile_topic, json.dumps(profile))
            
            logger.info(f"Profile sent to sensor {sensor_id}: {profile['profileID']}")
            
        except Exception as e:
            logger.error(f"Error handling connection request: {e}")
    
    def _handle_authentication(self, payload: str):
        """
        Handle sensor authentication (both username/password and certificate-based)
        
        Args:
            payload: JSON string containing authentication credentials
        """
        try:
            data = json.loads(payload)
            sensor_id = data.get('sensor_id')
            auth_type = data.get('auth_type', 'USERNAME_PASSWORD')
            
            logger.info(f"Authentication request from sensor {sensor_id} (type: {auth_type})")
            
            auth_success = False
            
            if auth_type == 'CERT_BASED':
                # Certificate-based authentication
                challenge = data.get('challenge')
                signature = data.get('signature')
                certificate_pem = data.get('certificate')
                
                if challenge and signature and certificate_pem:
                    # Verify the signature
                    auth_success = self._verify_certificate_auth(
                        challenge, signature, certificate_pem, sensor_id
                    )
                else:
                    logger.warning(f"Incomplete certificate-based auth data from sensor {sensor_id}")
            else:
                # Username/Password authentication
                username = data.get('username')
                password = data.get('password')
                
                # Mock authentication - in real implementation, verify credentials
                auth_success = username and password
            
            # Send authentication response
            auth_response = {
                'sensor_id': sensor_id,
                'authenticated': auth_success,
                'auth_type': auth_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            auth_topic = f"{MQTT_TOPIC_AUTH}/response/{sensor_id}"
            self.client.publish(auth_topic, json.dumps(auth_response))
            
            logger.info(f"Authentication response sent to sensor {sensor_id}: {auth_success} ({auth_type})")
            
        except Exception as e:
            logger.error(f"Error handling authentication: {e}")
    
    def _verify_certificate_auth(self, challenge_hex: str, signature_b64: str,
                                  certificate_pem: str, sensor_id: str) -> bool:
        """
        Verify certificate-based authentication
        
        Args:
            challenge_hex: Challenge in hex format
            signature_b64: Signature in base64 format
            certificate_pem: Certificate in PEM format
            sensor_id: Sensor ID
            
        Returns:
            bool: True if authentication is successful
        """
        try:
            # Load certificate
            cert = x509.load_pem_x509_certificate(
                certificate_pem.encode('utf-8'),
                default_backend()
            )
            
            # Get public key from certificate
            public_key = cert.public_key()
            
            # Convert challenge from hex to bytes
            challenge_bytes = bytes.fromhex(challenge_hex)
            
            # Decode signature from base64
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            public_key.verify(
                signature,
                challenge_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.info(f"Certificate-based authentication successful for sensor {sensor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Certificate-based authentication failed for sensor {sensor_id}: {e}")
    
    def _verify_data_signature(self, sensor_data: Dict[str, Any], signature_b64: str, sensor_id: str) -> bool:
        """
        Verify data signature for data trust
        
        Args:
            sensor_data: Sensor data dictionary
            signature_b64: Signature in base64 format
            sensor_id: Sensor ID
            
        Returns:
            bool: True if signature is valid
        """
        try:
            # Get sensor's certificate from connected sensors
            profile = self.connected_sensors.get(sensor_id)
            if not profile:
                return False
            
            # For now, we'll store certificate in profile during connection
            # In production, retrieve from certificate store
            certificate_pem = profile.get('certificate_pem')
            if not certificate_pem:
                logger.warning(f"No certificate found for sensor {sensor_id}")
                return False
            
            # Load certificate
            cert = x509.load_pem_x509_certificate(
                certificate_pem.encode('utf-8'),
                default_backend()
            )
            
            # Get public key
            public_key = cert.public_key()
            
            # Convert sensor data to JSON bytes (same format as signed)
            data_json = json.dumps(sensor_data).encode('utf-8')
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Verify signature
            public_key.verify(
                signature,
                data_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Data signature verification failed for sensor {sensor_id}: {e}")
            return False
            return False
    
    def _handle_sensor_data(self, payload: str):
        """
        Handle incoming sensor data with signature verification for data trust
        
        Args:
            payload: JSON string containing encrypted sensor data
        """
        try:
            data = json.loads(payload)
            sensor_id = data.get('sensor_id')
            encrypted_data = data.get('data')
            data_signature = data.get('data_signature')
            is_signed = data.get('signed', False)
            
            logger.info(f"Data received from sensor {sensor_id} (signed: {is_signed})")
            
            # Get sensor profile
            profile = self.connected_sensors.get(sensor_id)
            if not profile:
                logger.warning(f"No profile found for sensor {sensor_id}")
                return
            
            # Decrypt data if encryption is enabled
            if profile.get('supports_encryption') == BinaryFlag.YES:
                try:
                    decrypted_data = self.encryption.decrypt(encrypted_data)
                    sensor_data = json.loads(decrypted_data)
                except Exception as e:
                    logger.error(f"Failed to decrypt data from sensor {sensor_id}: {e}")
                    return
            else:
                sensor_data = json.loads(encrypted_data)
            
            # Verify data signature if present (DATA TRUST)
            data_trusted = False
            if is_signed and data_signature:
                # Get certificate from profile
                certificate_hash = profile.get('certificate_hash')
                if certificate_hash:
                    # Verify signature using sensor's certificate
                    data_trusted = self._verify_data_signature(
                        sensor_data, data_signature, sensor_id
                    )
                    if data_trusted:
                        logger.info(f"✓ Data signature verified for sensor {sensor_id} - DATA TRUSTED")
                    else:
                        logger.warning(f"✗ Data signature verification failed for sensor {sensor_id} - DATA NOT TRUSTED")
            
            # Prepare data for Data Lake with trust and traceability metadata
            data_lake_entry: dict[str, Any] = {
                'sensor_id': sensor_id,
                'profile_id': profile['profileID'],
                'timestamp': datetime.utcnow().isoformat(),
                'data_trusted': data_trusted,  # DATA TRUST indicator
                'data_signed': is_signed,
                'data_owner': sensor_data.get('data_owner', 'unknown'),  # TRACEABILITY: Data ownership
                'gateway_received_at': datetime.utcnow().isoformat(),  # TRACEABILITY: Receipt timestamp
                'data': sensor_data
            }
            logger.info("===================================================")
            logger.info(data_lake_entry)

            # Send to Data Lake
            if self.data_lake_callback:
                self.data_lake_callback(data_lake_entry)
                logger.info(f"Data from sensor {sensor_id} sent to Data Lake")
            else:
                logger.warning("No Data Lake callback configured")
                
        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")


if __name__ == "__main__":
    # Test the Gateway
    gateway = Gateway()
    gateway.start()
    
    try:
        # Keep running
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gateway.stop()

# Made with Bob
