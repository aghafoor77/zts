"""
Configuration settings for the IoT system
"""
import os

# MQTT Broker Settings
MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))
MQTT_KEEPALIVE = 60

# MQTT Topics
MQTT_TOPIC_CONNECT = "sensor/connect"
MQTT_TOPIC_PROFILE = "sensor/profile"
MQTT_TOPIC_DATA = "sensor/data"
MQTT_TOPIC_AUTH = "sensor/auth"

# MongoDB Settings
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'iot_data_lake')
MONGO_COLLECTION_DATA = 'sensor_data'
MONGO_COLLECTION_SCHEMAS = 'schemas'

# Consumer Gateway API Settings
CONSUMER_GATEWAY_HOST = os.getenv('CONSUMER_GATEWAY_HOST', '0.0.0.0')
CONSUMER_GATEWAY_PORT = int(os.getenv('CONSUMER_GATEWAY_PORT', 5012))

# Encryption Settings
AES_KEY = os.getenv('AES_KEY', 'ThisIsASecretKey')  # 16 bytes for AES-128
AES_MODE = 'CBC'

# Profile Schema Enums
class DeviceType:
    SENSOR = "sensor"
    CAMERA = "camera"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"

class MessageType:
    TELEMETRY = "telemetry"
    EVENT = "event"
    COMMAND = "command"

class Protocol:
    HTTP = "HTTP"
    MQTT = "MQTT"
    COAP = "CoAP"

class BinaryFlag:
    NO = 0
    YES = 1

class EncryptionType:
    DES = 0
    AES = 1
    TRIPLE_DES = 2

class AuthenticationType:
    USERNAME_PASSWORD = 0
    OAUTH = 1
    OTP = 2
    CERT_BASED = 3

class RecommendedProtocol:
    HTTP = 0
    MQTT = 1
    WEB_SOCKET = 2

# Made with # Com 
