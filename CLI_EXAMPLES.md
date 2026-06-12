# IoT Data Lake CLI - Usage Examples

This document provides detailed examples of using the CLI with real scenarios.

## Interactive Mode - Complete Example

### Scenario: Query sensor data from the last 24 hours

```bash
$ ./run_cli.sh interactive

=== IoT Data Lake Interactive Mode ===

Available Profiles:

1. profile_a1b2c3d4
2. profile_e5f6g7h8
3. profile_i9j0k1l2

Select a profile number: 1

Selected Profile: profile_a1b2c3d4

Show schema for this profile? [Y/n]: y

Sample Data Structure:
{
  "temperature": 25.5,
  "humidity": 55.0,
  "timestamp": "2026-06-11T10:30:00.000000"
}

==================================================
Query Parameters:
Use time range filter? [y/N]: y
Start time (e.g., "1h", "1d", or ISO format) [1h]: 1d
End time (ISO format, or press Enter for now): 
Maximum records [100]: 100

Found 144 records

Output format (table/json) [table]: table

+-------------+---------------------------+----------------------------------+
| Sensor ID   | Timestamp                 | Data                             |
+=============+===========================+==================================+
| sensor_001  | 2026-06-11T10:45:00.123Z  | {                                |
|             |                           |   "temperature": 24.8,           |
|             |                           |   "humidity": 52.3,              |
|             |                           |   "timestamp": "2026-06-11T1..." |
|             |                           | }                                |
+-------------+---------------------------+----------------------------------+
| sensor_001  | 2026-06-11T10:35:00.456Z  | {                                |
|             |                           |   "temperature": 25.2,           |
|             |                           |   "humidity": 54.1,              |
|             |                           |   "timestamp": "2026-06-11T1..." |
|             |                           | }                                |
+-------------+---------------------------+----------------------------------+
...
```

## Query Parameters Explained

### Time Range Filter Options

#### Option 1: Relative Time (Recommended for recent data)

```bash
Use time range filter? [y/N]: y
Start time (e.g., "1h", "1d", or ISO format) [1h]: 1h
```

**Relative Time Formats:**
- `1h` = Last 1 hour
- `2h` = Last 2 hours
- `30m` = Last 30 minutes
- `1d` = Last 1 day (24 hours)
- `2d` = Last 2 days
- `7d` = Last 7 days

#### Option 2: Absolute Time (ISO Format)

```bash
Use time range filter? [y/N]: y
Start time (e.g., "1h", "1d", or ISO format) [1h]: 2026-06-11T00:00:00
End time (ISO format, or press Enter for now): 2026-06-11T12:00:00
```

**ISO Format Examples:**
- `2026-06-11T00:00:00` - Midnight on June 11, 2026
- `2026-06-11T10:30:00` - 10:30 AM on June 11, 2026
- `2026-06-10T00:00:00` - Previous day

#### Option 3: No Time Filter (All data)

```bash
Use time range filter? [y/N]: n
Maximum records [100]: 50
```

This returns the most recent 50 records regardless of time.

### Maximum Records

```bash
Maximum records [100]: 200
```

Limits the number of records returned. Useful for:
- Quick previews: `10` or `20`
- Standard queries: `100` (default)
- Large datasets: `500` or `1000`

## Complete Examples

### Example 1: Last Hour of Data (Table Format)

```bash
$ ./run_cli.sh interactive

Available Profiles:
1. profile_temp_sensor_001

Select a profile number: 1
Selected Profile: profile_temp_sensor_001

Show schema for this profile? [Y/n]: n

Query Parameters:
Use time range filter? [y/N]: y
Start time (e.g., "1h", "1d", or ISO format) [1h]: 1h
End time (ISO format, or press Enter for now): 
Maximum records [100]: 50

Found 6 records

Output format (table/json) [table]: table

+-------------+---------------------------+----------------------------------+
| Sensor ID   | Timestamp                 | Data                             |
+=============+===========================+==================================+
| sensor_001  | 2026-06-11T11:10:00.000Z  | {"temperature": 26.5, "humidi... |
| sensor_001  | 2026-06-11T11:00:00.000Z  | {"temperature": 25.8, "humidi... |
| sensor_001  | 2026-06-11T10:50:00.000Z  | {"temperature": 25.2, "humidi... |
| sensor_001  | 2026-06-11T10:40:00.000Z  | {"temperature": 24.9, "humidi... |
| sensor_001  | 2026-06-11T10:30:00.000Z  | {"temperature": 24.5, "humidi... |
| sensor_001  | 2026-06-11T10:20:00.000Z  | {"temperature": 24.1, "humidi... |
+-------------+---------------------------+----------------------------------+
```

### Example 2: Last 24 Hours (JSON Format)

```bash
$ ./run_cli.sh interactive

Select a profile number: 1
Show schema for this profile? [Y/n]: n

Query Parameters:
Use time range filter? [y/N]: y
Start time (e.g., "1h", "1d", or ISO format) [1h]: 1d
End time (ISO format, or press Enter for now): 
Maximum records [100]: 100

Found 144 records

Output format (table/json) [table]: json

[
  {
    "sensor_id": "sensor_001",
    "profile_id": "profile_temp_sensor_001",
    "timestamp": "2026-06-11T11:10:00.000Z",
    "data": {
      "temperature": 26.5,
      "humidity": 58.2,
      "timestamp": "2026-06-11T11:10:00.000Z"
    }
  },
  {
    "sensor_id": "sensor_001",
    "profile_id": "profile_temp_sensor_001",
    "timestamp": "2026-06-11T11:00:00.000Z",
    "data": {
      "temperature": 25.8,
      "humidity": 56.7,
      "timestamp": "2026-06-11T11:00:00.000Z"
    }
  },
  ...
]
```

### Example 3: Specific Time Range

```bash
$ ./run_cli.sh interactive

Select a profile number: 1
Show schema for this profile? [Y/n]: n

Query Parameters:
Use time range filter? [y/N]: y
Start time (e.g., "1h", "1d", or ISO format) [1h]: 2026-06-11T08:00:00
End time (ISO format, or press Enter for now): 2026-06-11T10:00:00
Maximum records [100]: 100

Found 12 records

Output format (table/json) [table]: table

+-------------+---------------------------+----------------------------------+
| Sensor ID   | Timestamp                 | Data                             |
+=============+===========================+==================================+
| sensor_001  | 2026-06-11T09:50:00.000Z  | {"temperature": 23.8, "humidi... |
| sensor_001  | 2026-06-11T09:40:00.000Z  | {"temperature": 23.5, "humidi... |
...
```

### Example 4: All Available Data (Limited)

```bash
$ ./run_cli.sh interactive

Select a profile number: 1
Show schema for this profile? [Y/n]: n

Query Parameters:
Use time range filter? [y/N]: n
Maximum records [100]: 20

Found 20 records

Output format (table/json) [table]: table

[Shows most recent 20 records]
```

## Non-Interactive Examples

### Query with Command-Line Arguments

```bash
# Last hour, table format
./run_cli.sh query-data --profile-id profile_123 --start-time 1h --format table

# Last 24 hours, JSON format
./run_cli.sh query-data --profile-id profile_123 --start-time 1d --format json

# Specific time range
./run_cli.sh query-data \
  --profile-id profile_123 \
  --start-time "2026-06-11T00:00:00" \
  --end-time "2026-06-11T12:00:00" \
  --limit 200 \
  --format table

# Query by sensor ID
./run_cli.sh query-sensor --sensor-id sensor_001 --start-time 2h --limit 50
```

## Common Use Cases

### Use Case 1: Quick Health Check
```bash
./run_cli.sh health
```

### Use Case 2: See What Data is Available
```bash
./run_cli.sh list-profiles
./run_cli.sh list-schemas
```

### Use Case 3: Explore a Specific Profile
```bash
./run_cli.sh show-schema profile_123
```

### Use Case 4: Get Recent Data for Analysis
```bash
./run_cli.sh query-data --profile-id profile_123 --start-time 1h --format json > data.json
```

### Use Case 5: Monitor Sensor Over Time
```bash
# Get last 24 hours of data
./run_cli.sh query-sensor --sensor-id sensor_001 --start-time 1d --format table
```

### Use Case 6: View Trust and Traceability Information
```bash
# Query data with trust indicators
./run_cli.sh query-data --profile-id profile_123 --start-time 1h --show-trust

# Output includes:
# 🔐 TRUST & TRACEABILITY INFORMATION
# ============================================================
# 📊 Data Trust Statistics:
#   • Trusted Records: 95
#   • Signed Records: 95
#   • Trust Percentage: 95.0% ✓ Excellent
#
# 📋 Traceability:
#   • Consumer ID: cli_user_001
#   • Access Logged: ✓ Yes
```

### Use Case 7: Audit Data Access
```bash
# View all access logs
./run_cli.sh view-access-logs --limit 50

# Filter by consumer
./run_cli.sh view-access-logs --consumer-id user_001 --limit 20

# Filter by resource
./run_cli.sh view-access-logs --resource-id profile_123 --limit 30
```

### Use Case 8: Search Data by Content
```bash
# Search for specific values across all profiles
./run_cli.sh search-data --query "temperature"

# Search in specific profile
./run_cli.sh search-data --query "25.5" --profile-id profile_123

# Case-sensitive search
./run_cli.sh search-data --query "ERROR" --case-sensitive
```

### Use Case 9: Find Profiles by Schema Fields
```bash
# Find all profiles with a "temperature" field
./run_cli.sh search-schemas --field temperature

# Find profiles with specific field type
./run_cli.sh search-schemas --field humidity --field-type number

# Interactive: Query data from found profiles
./run_cli.sh search-schemas --field pressure
# Then select a profile to query its data
```

## New CLI Commands

### Trust and Traceability Commands

#### 1. Query Data with Trust Information
```bash
./run_cli.sh query-data \
  --profile-id profile_123 \
  --start-time 1h \
  --consumer-id my_app_001 \
  --show-trust
```

**Output:**
```
============================================================
🔐 TRUST & TRACEABILITY INFORMATION
============================================================

📊 Data Trust Statistics:
  • Trusted Records: 95
  • Signed Records: 95
  • Trust Percentage: 95.0% ✓ Excellent

📋 Traceability:
  • Consumer ID: my_app_001
  • Access Logged: ✓ Yes
============================================================

+-------------+---------------------------+----------+--------+---------------------------+
| Sensor ID   | Timestamp                 | Data     | Trusted| Signed | Owner            |
+=============+===========================+==========+========+========+==================+
| sensor_001  | 2026-06-11T10:45:00.123Z  | {...}    | ✓      | ✓      | TempCorp_TH-100  |
+-------------+---------------------------+----------+--------+---------------------------+
```

#### 2. View Access Logs
```bash
# All access logs
./run_cli.sh view-access-logs

# Filter by consumer
./run_cli.sh view-access-logs --consumer-id user_001

# Filter by resource
./run_cli.sh view-access-logs --resource-id profile_123

# Limit results
./run_cli.sh view-access-logs --limit 20
```

**Output:**
```
Access Logs (50 records)

+-------------+--------+---------------+-------------+---------------------------+
| Consumer ID | Action | Resource Type | Resource ID | Timestamp                 |
+=============+========+===============+=============+===========================+
| user_001    | query  | profile       | profile_123 | 2026-06-11T12:30:00.000Z  |
| user_002    | query  | sensor        | sensor_001  | 2026-06-11T12:25:00.000Z  |
+-------------+--------+---------------+-------------+---------------------------+
```

### Search Commands

#### 3. Search Data by String
```bash
# Search across all profiles
./run_cli.sh search-data --query "temperature"

# Search in specific profile
./run_cli.sh search-data --query "25.5" --profile-id profile_123

# Case-sensitive search
./run_cli.sh search-data --query "ERROR" --case-sensitive

# Limit search scope
./run_cli.sh search-data --query "humidity" --limit 50
```

**Output:**
```
Found 12 matching records

+-------------+---------------------------+----------+--------+--------+------------------+
| Sensor ID   | Timestamp                 | Data     | Trusted| Signed | Owner            |
+=============+===========================+==========+========+========+==================+
| sensor_001  | 2026-06-11T10:45:00.123Z  | {...}    | ✓      | ✓      | TempCorp_TH-100  |
+-------------+---------------------------+----------+--------+--------+------------------+
```

#### 4. Search Schemas by Field
```bash
# Find profiles with specific field
./run_cli.sh search-schemas --field temperature

# Filter by field type
./run_cli.sh search-schemas --field humidity --field-type number
```

**Output:**
```
Found 3 matching profiles

+------------------+-------------+--------+---------------------------+
| Profile ID       | Field       | Type   | Created At                |
+==================+=============+========+===========================+
| profile_123      | temperature | number | 2026-06-11T10:00:00.000Z  |
| profile_456      | temperature | number | 2026-06-11T09:00:00.000Z  |
| profile_789      | temperature | number | 2026-06-11T08:00:00.000Z  |
+------------------+-------------+--------+---------------------------+

Query data from a profile? [y/N]: y
Enter profile number (1-3): 1

Querying data from profile_123...

[Shows trust info and data table]
```

## Tips and Best Practices

1. **Start with Interactive Mode**: It's easier to explore data
   ```bash
   ./run_cli.sh interactive
   ```

2. **Use Relative Times**: For recent data, use `1h`, `1d` instead of ISO timestamps

3. **Limit Results**: Start with small limits (10-20) to preview data structure

4. **Export to JSON**: For further processing or analysis
   ```bash
   ./run_cli.sh query-data --profile-id profile_123 --start-time 1d --format json > output.json
   ```

5. **Check Schema First**: Understand data structure before querying
   ```bash
   ./run_cli.sh show-schema profile_123
   ```

## Troubleshooting Examples

### No Data Found
```bash
Found 0 records
```
**Solutions:**
- Wait longer for sensors to send data
- Check if Docker services are running: `docker-compose ps`
- Try a longer time range: `1d` instead of `1h`

### Invalid Profile ID
```bash
Error: Schema not found for profile: profile_xyz
```
**Solution:**
- List available profiles: `./run_cli.sh list-profiles`
- Use a valid profile ID from the list

### Connection Error
```bash
Error connecting to Consumer Gateway
```
**Solutions:**
- Ensure Docker services are running: `docker-compose up -d`
- Check Consumer Gateway: `docker-compose logs consumer_gateway`
- Verify port 5000 is not in use: `netstat -an | grep 5000`

---

