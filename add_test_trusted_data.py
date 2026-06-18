#!/usr/bin/env python3
"""
Quick script to add test data with trust metadata
This demonstrates the trust and traceability features
"""

from data_lake.data_lake import DataLake
from datetime import datetime, timedelta
import random

def add_trusted_test_data():
    """Add test sensor data with trust metadata"""
    
    print("Adding test data with trust metadata...")
    print("=" * 60)
    
    data_lake = DataLake()
    
    # Create test profile
    test_profile_id = "test_temperature_profile"
    
    # Add 20 records: 15 trusted, 5 untrusted
    records_added = 0
    trusted_count = 0
    signed_count = 0
    
    for i in range(20):
        # 75% trusted, 90% signed
        is_trusted = i < 15
        is_signed = i < 18
        
        timestamp = datetime.utcnow() - timedelta(minutes=20-i)
        
        test_data = {
            "sensor_id": f"test_sensor_{(i % 3) + 1:03d}",
            "profile_id": test_profile_id,
            "timestamp": timestamp,
            "data": {
                "temperature": round(20 + random.uniform(-5, 10), 2),
                "humidity": round(50 + random.uniform(-10, 20), 2),
                "pressure": round(1013 + random.uniform(-5, 5), 2)
            },
            "data_trusted": is_trusted,
            "data_signed": is_signed,
            "data_owner": f"test_sensor_{(i % 3) + 1:03d}" if is_trusted else "unknown"
        }
        
        if is_signed:
            test_data["signature"] = f"mock_signature_{i:04d}_xyz"
        
        # Use store_data method and include trust metadata
        data_entry = {
            "sensor_id": test_data["sensor_id"],
            "profile_id": test_data["profile_id"],
            "timestamp": test_data["timestamp"],
            "data": test_data["data"]
        }
        
        # Insert with trust metadata directly
        document = {
            **data_entry,
            "data_trusted": test_data["data_trusted"],
            "data_signed": test_data["data_signed"],
            "data_owner": test_data["data_owner"]
        }
        
        if "signature" in test_data:
            document["signature"] = test_data["signature"]
        
        data_lake.data_collection.insert_one(document)
        
        # Generate schema if first record
        if records_added == 0:
            data_lake._generate_and_store_schema(test_profile_id, test_data["data"])
        records_added += 1
        
        if is_trusted:
            trusted_count += 1
        if is_signed:
            signed_count += 1
    
    print(f"✓ Added {records_added} test records")
    print(f"  - Trusted: {trusted_count} ({trusted_count/records_added*100:.1f}%)")
    print(f"  - Signed: {signed_count} ({signed_count/records_added*100:.1f}%)")
    print(f"  - Profile ID: {test_profile_id}")
    print()
    print("=" * 60)
    print("Test data added successfully!")
    print()
    print("Now you can:")
    print(f"1. View in CLI:")
    print(f"   python -m cli.cli query-data --profile-id {test_profile_id} --show-trust")
    print()
    print(f"2. View in Web Interface:")
    print(f"   http://localhost:3000")
    print(f"   - Select '{test_profile_id}' in Data Explorer")
    print()
    print(f"3. Check via API:")
    print(f"   curl 'http://localhost:5012/api/data/profile/{test_profile_id}?limit=20'")
    print()
    print("Trust Score should show: ~75% (15/20 trusted records)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        add_trusted_test_data()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure MongoDB is running:")
        print("  docker compose ps mongodb")
        print("  docker compose logs mongodb")

