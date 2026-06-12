#!/bin/bash

echo "=========================================="
echo "Clean Data Lake - Remove All Records"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will delete ALL data from MongoDB!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "Cleaning Data Lake..."
echo ""

# Connect to MongoDB and clean collections
docker compose exec -T mongodb mongosh --quiet << 'EOF'
use iot_data_lake

// Delete all sensor data
print("Deleting sensor data...");
var result1 = db.sensor_data.deleteMany({});
print("✓ Deleted " + result1.deletedCount + " sensor data records");

// Delete all schemas
print("Deleting schemas...");
var result2 = db.schemas.deleteMany({});
print("✓ Deleted " + result2.deletedCount + " schemas");

// Delete all access logs
print("Deleting access logs...");
var result3 = db.access_logs.deleteMany({});
print("✓ Deleted " + result3.deletedCount + " access logs");

// Show remaining counts
print("");
print("Remaining records:");
print("- Sensor data: " + db.sensor_data.countDocuments({}));
print("- Schemas: " + db.schemas.countDocuments({}));
print("- Access logs: " + db.access_logs.countDocuments({}));

EOF

echo ""
echo "=========================================="
echo "✓ Data Lake cleaned successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart sensor to generate new data:"
echo "   docker compose restart sensor_simulator"
echo ""
echo "2. Or add test data:"
echo "   python add_test_trusted_data.py"
echo ""
echo "3. Verify in web interface:"
echo "   http://localhost:3000"

# Made with Bob
