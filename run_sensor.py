"""
Sensor Runner Script
Starts a sensor simulator that connects to the Gateway
"""
import os
import logging
import time
from sensor.sensor import Sensor, generate_temperature_data
from config.sensor_credentials import SENSOR_CERTIFICATE_PEM, SENSOR_PRIVATE_KEY_PEM

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the Sensor"""
    # Get configuration from environment variables
    sensor_id = os.getenv('SENSOR_ID', 'sensor_001')
    device_type = os.getenv('DEVICE_TYPE', 'sensor')
    manufacturer = os.getenv('MANUFACTURER', 'TempCorp')
    model = os.getenv('MODEL', 'TH-100')
    
    # Self-signed certificate and private key in PEM format
    certificate = os.getenv('CERTIFICATE', SENSOR_CERTIFICATE_PEM)
    private_key = os.getenv('PRIVATE_KEY', SENSOR_PRIVATE_KEY_PEM)
    
    logger.info(f"Starting Sensor: {sensor_id}")
    
    # Initialize Sensor with certificate and private key
    sensor = Sensor(
        sensor_id=sensor_id,
        device_type=device_type,
        manufacturer=manufacturer,
        model=model,
        certificate=certificate,
        private_key_pem=private_key
    )
    
    # Connect to Gateway
    sensor.connect()
    
    # Wait for profile and authentication
    logger.info("Waiting for profile and authentication...")
    time.sleep(5)
    
    # Start sending data
    logger.info("Starting data transmission...")
    try:
        sensor.start_sending_data(generate_temperature_data, interval=10)
    except KeyboardInterrupt:
        logger.info("Shutting down Sensor...")
        sensor.disconnect()
        logger.info("Sensor stopped.")


if __name__ == "__main__":
    main()

# Made with # Com 
