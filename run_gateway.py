"""
Gateway Runner Script
Starts the Gateway service and connects it to the Data Lake
"""
import logging
import time
from gateway.gateway import Gateway
from data_lake.data_lake import DataLake

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the Gateway"""
    logger.info("Starting Gateway Service...")
    
    # Initialize Data Lake
    data_lake = DataLake()
    
    # Initialize Gateway with Data Lake callback
    gateway = Gateway(data_lake_callback=data_lake.store_data)
    
    # Start Gateway
    gateway.start()
    
    logger.info("Gateway Service is running. Press Ctrl+C to stop.")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Gateway Service...")
        gateway.stop()
        data_lake.close()
        logger.info("Gateway Service stopped.")


if __name__ == "__main__":
    main()

# Made with Bob
