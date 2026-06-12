"""
Consumer Gateway - REST API for CLI Access
Provides API endpoints for retrieving schemas and sensor data
"""
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any
from data_lake.data_lake import DataLake
from config.config import CONSUMER_GATEWAY_HOST, CONSUMER_GATEWAY_PORT
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize Data Lake connection
data_lake = DataLake()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Consumer Gateway'}), 200


@app.route('/api/schemas', methods=['GET'])
def get_schemas():
    """
    Get all available schemas
    
    Returns:
        JSON response with list of schemas
    """
    try:
        schemas = data_lake.get_all_schemas()
        return jsonify({
            'success': True,
            'count': len(schemas),
            'schemas': schemas
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving schemas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/schemas/<profile_id>', methods=['GET'])
def get_schema_by_profile(profile_id: str):
    """
    Get schema for a specific profile
    
    Args:
        profile_id: Profile ID
        
    Returns:
        JSON response with schema
    """
    try:
        schema = data_lake.get_schema_by_profile(profile_id)
        if schema:
            return jsonify({
                'success': True,
                'schema': schema
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Schema not found'
            }), 404
    except Exception as e:
        logger.error(f"Error retrieving schema for profile {profile_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/profile/<profile_id>', methods=['GET'])
def get_data_by_profile(profile_id: str):
    """
    Get sensor data for a specific profile with traceability logging
    
    Query Parameters:
        start_time: Start timestamp (ISO format)
        end_time: End timestamp (ISO format)
        limit: Maximum number of records (default: 100)
        consumer_id: Consumer identifier (optional, for traceability)
        
    Args:
        profile_id: Profile ID
        
    Returns:
        JSON response with sensor data and trust indicators
    """
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 100))
        consumer_id = request.args.get('consumer_id', f'anonymous_{uuid.uuid4().hex[:8]}')
        
        # TRACEABILITY: Log data access
        data_lake.log_data_access(
            consumer_id=consumer_id,
            action='query',
            resource_type='profile',
            resource_id=profile_id,
            metadata={
                'start_time': start_time,
                'end_time': end_time,
                'limit': limit,
                'ip_address': request.remote_addr
            }
        )
        
        data = data_lake.get_data_by_profile(
            profile_id=profile_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        # Get total count without limit for accurate statistics
        total_data = data_lake.get_data_by_profile(
            profile_id=profile_id,
            start_time=start_time,
            end_time=end_time,
            limit=999999  # Very large limit to get all records
        )
        
        # Calculate trust statistics from ALL data (not just limited results)
        total_count = len(total_data)
        trusted_count = sum(1 for d in total_data if d.get('data_trusted', False))
        signed_count = sum(1 for d in total_data if d.get('data_signed', False))
        
        return jsonify({
            'success': True,
            'count': len(data),  # Number of records returned
            'total_count': total_count,  # Total records in database
            'profile_id': profile_id,
            'trust_info': {  # DATA TRUST information (from ALL data)
                'trusted_records': trusted_count,
                'signed_records': signed_count,
                'trust_percentage': (trusted_count / total_count * 100) if total_count > 0 else 0
            },
            'traceability': {  # TRACEABILITY information
                'consumer_id': consumer_id,
                'access_logged': True
            },
            'data': data
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving data for profile {profile_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/sensor/<sensor_id>', methods=['GET'])
def get_data_by_sensor(sensor_id: str):
    """
    Get data for a specific sensor
    
    Query Parameters:
        start_time: Start timestamp (ISO format)
        end_time: End timestamp (ISO format)
        limit: Maximum number of records (default: 100)
        
    Args:
        sensor_id: Sensor ID
        
    Returns:
        JSON response with sensor data
    """
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 100))
        
        data = data_lake.get_data_by_sensor(
            sensor_id=sensor_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'count': len(data),
            'sensor_id': sensor_id,
            'data': data
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving data for sensor {sensor_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/access-logs', methods=['GET'])
def get_access_logs():
    """
    Get access logs for traceability auditing
    
    Query Parameters:
        consumer_id: Filter by consumer ID (optional)
        resource_id: Filter by resource ID (optional)
        limit: Maximum number of logs (default: 100)
        
    Returns:
        JSON response with access logs
    """
    try:
        consumer_id = request.args.get('consumer_id')
        resource_id = request.args.get('resource_id')
        limit = int(request.args.get('limit', 100))
        
        logs = data_lake.get_access_logs(
            consumer_id=consumer_id,
            resource_id=resource_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': logs
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving access logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """
    Get list of unique profile IDs
    
    Returns:
        JSON response with list of profile IDs
    """
    try:
        schemas = data_lake.get_all_schemas()
        profile_ids = [schema['profile_id'] for schema in schemas]
        
        return jsonify({
            'success': True,
            'count': len(profile_ids),
            'profile_ids': profile_ids
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving profile IDs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def start_consumer_gateway():
    """Start the Consumer Gateway API server"""
    logger.info(f"Starting Consumer Gateway on {CONSUMER_GATEWAY_HOST}:{CONSUMER_GATEWAY_PORT}")
    app.run(
        host=CONSUMER_GATEWAY_HOST,
        port=CONSUMER_GATEWAY_PORT,
        debug=False
    )


if __name__ == "__main__":
    start_consumer_gateway()

# Made with Bob
