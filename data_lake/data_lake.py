"""
Data Lake Module - NoSQL Storage with Schema Generation
Stores sensor data in MongoDB and automatically generates JSON schemas
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pymongo import MongoClient
from genson import SchemaBuilder
from config.config import (
    MONGO_HOST, MONGO_PORT, MONGO_DB_NAME,
    MONGO_COLLECTION_DATA, MONGO_COLLECTION_SCHEMAS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLake:
    """
    Data Lake for storing sensor data and managing schemas
    """
    
    def __init__(self):
        """Initialize the Data Lake with MongoDB connection"""
        try:
            self.client = MongoClient(MONGO_HOST, MONGO_PORT)
            self.db = self.client[MONGO_DB_NAME]
            self.data_collection = self.db[MONGO_COLLECTION_DATA]
            self.schema_collection = self.db[MONGO_COLLECTION_SCHEMAS]
            self.access_log_collection = self.db['access_logs']  # TRACEABILITY: Access logs
            
            # Create indexes for efficient querying
            self.data_collection.create_index([("sensor_id", 1), ("timestamp", -1)])
            self.data_collection.create_index([("profile_id", 1)])
            self.data_collection.create_index([("data_trusted", 1)])  # Index for trusted data queries
            self.schema_collection.create_index([("profile_id", 1)], unique=True)
            self.access_log_collection.create_index([("timestamp", -1)])  # TRACEABILITY: Access log index
            self.access_log_collection.create_index([("consumer_id", 1)])
            
            logger.info("Data Lake initialized successfully with traceability support")
        except Exception as e:
            logger.error(f"Failed to initialize Data Lake: {e}")
            raise
    
    def store_data(self, data_entry: Dict[str, Any]):
        """
        Store sensor data in the Data Lake with trust and traceability metadata
        
        Args:
            data_entry: Dictionary containing sensor_id, profile_id, timestamp, data,
                       and optional trust metadata (data_trusted, data_signed, data_owner, etc.)
        """
        try:
            sensor_id = data_entry.get('sensor_id')
            profile_id = data_entry.get('profile_id')
            timestamp = data_entry.get('timestamp')
            sensor_data = data_entry.get('data')
            
            # Check if this is the first data from this profile
            if not self._schema_exists(profile_id):
                logger.info(f"First data from profile {profile_id}, generating schema")
                self._generate_and_store_schema(profile_id, sensor_data)
            
            # Store the data with ALL metadata including trust and traceability fields
            document = {
                'sensor_id': sensor_id,
                'profile_id': profile_id,
                'timestamp': timestamp,
                'data': sensor_data,
                # DATA TRUST metadata
                'data_trusted': data_entry.get('data_trusted', False),
                'data_signed': data_entry.get('data_signed', False),
                'data_owner': data_entry.get('data_owner', 'unknown'),
                # TRACEABILITY metadata
                'gateway_received_at': data_entry.get('gateway_received_at'),
            }
            
            # Add optional signature if present
            if 'signature' in data_entry:
                document['signature'] = data_entry['signature']
            
            result = self.data_collection.insert_one(document)
            
            # Log with trust info
            trust_status = "✓ TRUSTED" if document['data_trusted'] else "✗ NOT TRUSTED"
            signed_status = "SIGNED" if document['data_signed'] else "UNSIGNED"
            logger.info(f"Data stored with ID: {result.inserted_id} | {trust_status} | {signed_status} | Owner: {document['data_owner']}")
            
        except Exception as e:
            logger.error(f"Error storing data: {e}")
            raise
    
    def _schema_exists(self, profile_id: str) -> bool:
        """
        Check if a schema exists for the given profile ID
        
        Args:
            profile_id: Profile ID to check
            
        Returns:
            bool: True if schema exists
        """
        return self.schema_collection.find_one({'profile_id': profile_id}) is not None
    
    def _generate_and_store_schema(self, profile_id: str, sample_data: Dict[str, Any]):
        """
        Generate JSON schema from sample data and store it
        
        Args:
            profile_id: Profile ID associated with the schema
            sample_data: Sample data to generate schema from
        """
        try:
            # Generate schema using genson
            builder = SchemaBuilder()
            builder.add_object(sample_data)
            schema = builder.to_schema()
            
            # Store schema
            schema_document = {
                'profile_id': profile_id,
                'schema': schema,
                'created_at': datetime.utcnow().isoformat(),
                'sample_data': sample_data
            }
            
            self.schema_collection.insert_one(schema_document)
            logger.info(f"Schema generated and stored for profile {profile_id}")
            
        except Exception as e:
            logger.error(f"Error generating schema: {e}")
            raise
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all available schemas
        
        Returns:
            List of schema documents
        """
        try:
            schemas = list(self.schema_collection.find({}, {'_id': 0}))
            logger.info(f"Retrieved {len(schemas)} schemas")
            return schemas
        except Exception as e:
            logger.error(f"Error retrieving schemas: {e}")
            return []
    
    def get_schema_by_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for a specific profile
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Schema document or None
        """
        try:
            schema = self.schema_collection.find_one({'profile_id': profile_id}, {'_id': 0})
            return schema
        except Exception as e:
            logger.error(f"Error retrieving schema for profile {profile_id}: {e}")
            return None
    
    def get_data_by_profile(self, profile_id: str, start_time: str = None, 
                           end_time: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get sensor data for a specific profile within a time range
        
        Args:
            profile_id: Profile ID
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            limit: Maximum number of records to return
            
        Returns:
            List of data documents
        """
        try:
            query = {'profile_id': profile_id}
            
            # Add time range filter if provided
            if start_time or end_time:
                time_filter = {}
                if start_time:
                    time_filter['$gte'] = start_time
                if end_time:
                    time_filter['$lte'] = end_time
                query['timestamp'] = time_filter
            
            # Query data
            data = list(self.data_collection.find(
                query,
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
            
            logger.info(f"Retrieved {len(data)} records for profile {profile_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error retrieving data for profile {profile_id}: {e}")
            return []
    
    def get_data_by_sensor(self, sensor_id: str, start_time: str = None,
                          end_time: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get data for a specific sensor within a time range
        
        Args:
            sensor_id: Sensor ID
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            limit: Maximum number of records to return
            
        Returns:
            List of data documents
        """
        try:
            query = {'sensor_id': sensor_id}
            
            # Add time range filter if provided
            if start_time or end_time:
                time_filter = {}
                if start_time:
                    time_filter['$gte'] = start_time
                if end_time:
                    time_filter['$lte'] = end_time
                query['timestamp'] = time_filter
            
            # Query data
            data = list(self.data_collection.find(
                query,
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
            
            logger.info(f"Retrieved {len(data)} records for sensor {sensor_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error retrieving data for sensor {sensor_id}: {e}")
            return []
    
    def log_data_access(self, consumer_id: str, action: str, resource_type: str, 
                       resource_id: str, metadata: Dict[str, Any] = None):
        """
        Log data access for traceability
        
        Args:
            consumer_id: ID of the consumer accessing the data
            action: Action performed (e.g., 'read', 'query', 'export')
            resource_type: Type of resource accessed (e.g., 'profile', 'sensor', 'schema')
            resource_id: ID of the resource accessed
            metadata: Additional metadata about the access
        """
        try:
            access_log = {
                'consumer_id': consumer_id,
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
            self.access_log_collection.insert_one(access_log)
            logger.info(f"Access logged: {consumer_id} performed {action} on {resource_type}/{resource_id}")
            
        except Exception as e:
            logger.error(f"Error logging access: {e}")
    
    def get_access_logs(self, consumer_id: str = None, resource_id: str = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve access logs for traceability auditing
        
        Args:
            consumer_id: Filter by consumer ID (optional)
            resource_id: Filter by resource ID (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of access log entries
        """
        try:
            query = {}
            if consumer_id:
                query['consumer_id'] = consumer_id
            if resource_id:
                query['resource_id'] = resource_id
            
            logs = list(self.access_log_collection.find(
                query,
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
            
            logger.info(f"Retrieved {len(logs)} access logs")
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving access logs: {e}")
            return []
    
    def close(self):
        """Close the MongoDB connection"""
        self.client.close()
        logger.info("Data Lake connection closed")


if __name__ == "__main__":
    # Test the Data Lake
    data_lake = DataLake()
    
    # Test data
    test_entry = {
        'sensor_id': 'sensor_001',
        'profile_id': 'test_profile_123',
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'temperature': 25.5,
            'humidity': 55.0,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    # Store data
    data_lake.store_data(test_entry)
    
    # Get schemas
    schemas = data_lake.get_all_schemas()
    print(f"Schemas: {json.dumps(schemas, indent=2)}")
    
    # Get data
    data = data_lake.get_data_by_profile('test_profile_123')
    print(f"Data: {json.dumps(data, indent=2)}")
    
    data_lake.close()

# Made with # Com 
