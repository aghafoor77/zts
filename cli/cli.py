"""
CLI Module - Command Line Interface for Data Access
Provides interactive CLI for querying sensor data with trust and traceability features
"""
import click
import requests
import json
from typing import List, Dict, Any
from tabulate import tabulate
from datetime import datetime, timedelta
from dateutil import parser
from config.config import CONSUMER_GATEWAY_HOST, CONSUMER_GATEWAY_PORT
import re

# Consumer Gateway API base URL
API_BASE_URL = f"http://{CONSUMER_GATEWAY_HOST}:{CONSUMER_GATEWAY_PORT}/api"


@click.group()
def cli():
    """IoT Data Lake CLI - Access sensor data and schemas"""
    pass


@cli.command()
def health():
    """Check Consumer Gateway health status"""
    try:
        response = requests.get(f"http://{CONSUMER_GATEWAY_HOST}:{CONSUMER_GATEWAY_PORT}/health")
        if response.status_code == 200:
            data = response.json()
            click.echo(click.style(f"✓ {data['service']} is {data['status']}", fg='green'))
        else:
            click.echo(click.style(f"✗ Health check failed: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"✗ Error connecting to Consumer Gateway: {e}", fg='red'))


@cli.command()
def list_schemas():
    """List all available schemas"""
    try:
        response = requests.get(f"{API_BASE_URL}/schemas")
        if response.status_code == 200:
            data = response.json()
            schemas = data['schemas']
            
            if not schemas:
                click.echo("No schemas available")
                return
            
            # Prepare table data
            table_data = []
            for schema in schemas:
                table_data.append([
                    schema['profile_id'],
                    schema.get('created_at', 'N/A'),
                    json.dumps(schema.get('sample_data', {}), indent=2)[:100] + '...'
                ])
            
            click.echo(f"\nAvailable Schemas ({data['count']}):\n")
            click.echo(tabulate(
                table_data,
                headers=['Profile ID', 'Created At', 'Sample Data'],
                tablefmt='grid'
            ))
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
@click.argument('profile_id')
def show_schema(profile_id):
    """Show detailed schema for a specific profile"""
    try:
        response = requests.get(f"{API_BASE_URL}/schemas/{profile_id}")
        if response.status_code == 200:
            data = response.json()
            schema = data['schema']
            
            click.echo(f"\nSchema for Profile: {profile_id}\n")
            click.echo(json.dumps(schema['schema'], indent=2))
            
            click.echo(f"\nSample Data:\n")
            click.echo(json.dumps(schema.get('sample_data', {}), indent=2))
        elif response.status_code == 404:
            click.echo(click.style(f"Schema not found for profile: {profile_id}", fg='yellow'))
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
def list_profiles():
    """List all available profile IDs"""
    try:
        response = requests.get(f"{API_BASE_URL}/profiles")
        if response.status_code == 200:
            data = response.json()
            profile_ids = data['profile_ids']
            
            if not profile_ids:
                click.echo("No profiles available")
                return
            
            click.echo(f"\nAvailable Profiles ({data['count']}):\n")
            for i, profile_id in enumerate(profile_ids, 1):
                click.echo(f"{i}. {profile_id}")
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
@click.option('--profile-id', prompt='Profile ID', help='Profile ID to query')
@click.option('--start-time', default=None, help='Start time (ISO format or relative like "1h", "1d")')
@click.option('--end-time', default=None, help='End time (ISO format)')
@click.option('--limit', default=100, help='Maximum number of records')
@click.option('--consumer-id', default=None, help='Consumer ID for traceability')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--show-trust', is_flag=True, help='Show trust and traceability information')
def query_data(profile_id, start_time, end_time, limit, consumer_id, output_format, show_trust):
    """Query sensor data for a specific profile with trust and traceability"""
    try:
        # Parse relative time if provided
        if start_time:
            start_time = parse_time(start_time)
        if end_time:
            end_time = parse_time(end_time)
        
        # Build query parameters
        params = {'limit': limit}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if consumer_id:
            params['consumer_id'] = consumer_id
        
        response = requests.get(f"{API_BASE_URL}/data/profile/{profile_id}", params=params)
        
        if response.status_code == 200:
            data = response.json()
            records = data['data']
            
            if not records:
                click.echo("No data found")
                return
            
            # Display trust and traceability info
            if show_trust or output_format == 'table':
                display_trust_info(data)
            
            if output_format == 'json':
                click.echo(json.dumps(data, indent=2))
            else:
                # Display as table
                display_data_table(records, show_trust=show_trust)
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
@click.option('--sensor-id', prompt='Sensor ID', help='Sensor ID to query')
@click.option('--start-time', default=None, help='Start time (ISO format or relative like "1h", "1d")')
@click.option('--end-time', default=None, help='End time (ISO format)')
@click.option('--limit', default=100, help='Maximum number of records')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
def query_sensor(sensor_id, start_time, end_time, limit, output_format):
    """Query data for a specific sensor"""
    try:
        # Parse relative time if provided
        if start_time:
            start_time = parse_time(start_time)
        if end_time:
            end_time = parse_time(end_time)
        
        # Build query parameters
        params = {'limit': limit}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        response = requests.get(f"{API_BASE_URL}/data/sensor/{sensor_id}", params=params)
        
        if response.status_code == 200:
            data = response.json()
            records = data['data']
            
            if not records:
                click.echo("No data found")
                return
            
            if output_format == 'json':
                click.echo(json.dumps(records, indent=2))
            else:
                # Display as table
                display_data_table(records)
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
@click.option('--consumer-id', default=None, help='Filter by consumer ID')
@click.option('--resource-id', default=None, help='Filter by resource ID')
@click.option('--limit', default=50, help='Maximum number of logs')
def view_access_logs(consumer_id, resource_id, limit):
    """View access logs for traceability auditing"""
    try:
        params = {'limit': limit}
        if consumer_id:
            params['consumer_id'] = consumer_id
        if resource_id:
            params['resource_id'] = resource_id
        
        response = requests.get(f"{API_BASE_URL}/access-logs", params=params)
        
        if response.status_code == 200:
            data = response.json()
            logs = data['logs']
            
            if not logs:
                click.echo("No access logs found")
                return
            
            count = data['count']
            click.echo(f"\n{click.style(f'Access Logs ({count} records)', fg='cyan', bold=True)}\n")
            
            # Prepare table data
            table_data = []
            for log in logs:
                table_data.append([
                    log.get('consumer_id', 'N/A'),
                    log.get('action', 'N/A'),
                    log.get('resource_type', 'N/A'),
                    log.get('resource_id', 'N/A'),
                    log.get('timestamp', 'N/A')
                ])
            
            click.echo(tabulate(
                table_data,
                headers=['Consumer ID', 'Action', 'Resource Type', 'Resource ID', 'Timestamp'],
                tablefmt='grid'
            ))
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
@click.option('--query', prompt='Search query', help='String to search for in data')
@click.option('--profile-id', default=None, help='Limit search to specific profile')
@click.option('--limit', default=100, help='Maximum number of records to search')
@click.option('--case-sensitive', is_flag=True, help='Case-sensitive search')
def search_data(query, profile_id, limit, case_sensitive):
    """Search for data containing specific string patterns"""
    try:
        # Get data to search
        records = []
        if profile_id:
            response = requests.get(f"{API_BASE_URL}/data/profile/{profile_id}", params={'limit': limit})
            if response.status_code == 200:
                records = response.json()['data']
        else:
            # Get all profiles and search across them
            profiles_response = requests.get(f"{API_BASE_URL}/profiles")
            if profiles_response.status_code != 200:
                click.echo(click.style("Error fetching profiles", fg='red'))
                return
            
            profile_ids = profiles_response.json()['profile_ids']
            
            for pid in profile_ids:
                resp = requests.get(f"{API_BASE_URL}/data/profile/{pid}", params={'limit': limit})
                if resp.status_code == 200:
                    records.extend(resp.json()['data'])
        
        if not records:
            click.echo("No data to search")
            return
        
        # Search through records
        matching_records = []
        search_query = query if case_sensitive else query.lower()
        
        for record in records:
            # Convert record to JSON string for searching
            record_str = json.dumps(record)
            if not case_sensitive:
                record_str = record_str.lower()
            
            if search_query in record_str:
                matching_records.append(record)
        
        if not matching_records:
            click.echo(click.style(f"No matches found for '{query}'", fg='yellow'))
            return
        
        click.echo(f"\n{click.style(f'Found {len(matching_records)} matching records', fg='green', bold=True)}\n")
        
        # Display matching records
        display_data_table(matching_records, show_trust=True)
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


@cli.command()
@click.option('--field', prompt='Field name to search', help='Field name in schema (e.g., temperature, humidity)')
@click.option('--field-type', default=None, help='Filter by field type (string, number, boolean)')
def search_schemas(field, field_type):
    """Search schemas to find profiles with specific fields"""
    try:
        response = requests.get(f"{API_BASE_URL}/schemas")
        
        if response.status_code == 200:
            data = response.json()
            schemas = data['schemas']
            
            if not schemas:
                click.echo("No schemas available")
                return
            
            # Search through schemas
            matching_profiles = []
            
            for schema in schemas:
                schema_def = schema.get('schema', {})
                properties = schema_def.get('properties', {})
                
                # Check if field exists in schema
                if field in properties:
                    field_info = properties[field]
                    
                    # Filter by type if specified
                    if field_type:
                        if field_info.get('type') == field_type:
                            matching_profiles.append({
                                'profile_id': schema['profile_id'],
                                'field': field,
                                'type': field_info.get('type', 'N/A'),
                                'created_at': schema.get('created_at', 'N/A')
                            })
                    else:
                        matching_profiles.append({
                            'profile_id': schema['profile_id'],
                            'field': field,
                            'type': field_info.get('type', 'N/A'),
                            'created_at': schema.get('created_at', 'N/A')
                        })
            
            if not matching_profiles:
                click.echo(click.style(f"No profiles found with field '{field}'", fg='yellow'))
                return
            
            click.echo(f"\n{click.style(f'Found {len(matching_profiles)} matching profiles', fg='green', bold=True)}\n")
            
            # Display matching profiles
            table_data = []
            for profile in matching_profiles:
                table_data.append([
                    profile['profile_id'],
                    profile['field'],
                    profile['type'],
                    profile['created_at']
                ])
            
            click.echo(tabulate(
                table_data,
                headers=['Profile ID', 'Field', 'Type', 'Created At'],
                tablefmt='grid'
            ))
            
            # Offer to query data from selected profile
            if click.confirm('\nQuery data from a profile?', default=False):
                click.echo("\nYou can enter either:")
                click.echo("  • Profile number (1-{})".format(len(matching_profiles)))
                click.echo("  • Profile ID directly (e.g., profile_123)")
                
                selection_input = click.prompt('\nEnter your choice', type=str)
                
                # Try to parse as integer first (profile number)
                selected_profile = None
                try:
                    selection = int(selection_input)
                    if 1 <= selection <= len(matching_profiles):
                        selected_profile = matching_profiles[selection - 1]['profile_id']
                    else:
                        click.echo(click.style(f"Invalid profile number. Must be between 1 and {len(matching_profiles)}", fg='red'))
                        return
                except ValueError:
                    # Not a number, treat as profile ID
                    # Check if it's in the matching profiles
                    profile_ids = [p['profile_id'] for p in matching_profiles]
                    if selection_input in profile_ids:
                        selected_profile = selection_input
                    else:
                        click.echo(click.style(f"Profile ID '{selection_input}' not found in search results", fg='red'))
                        click.echo("Available profile IDs:")
                        for i, pid in enumerate(profile_ids, 1):
                            click.echo(f"  {i}. {pid}")
                        return
                
                if selected_profile:
                    click.echo(f"\nQuerying data from {click.style(selected_profile, fg='cyan')}...")
                    
                    # Query data
                    data_response = requests.get(f"{API_BASE_URL}/data/profile/{selected_profile}", params={'limit': 10})
                    if data_response.status_code == 200:
                        result = data_response.json()
                        display_trust_info(result)
                        display_data_table(result['data'], show_trust=True)
                    else:
                        click.echo(click.style(f"Error querying data: {data_response.status_code}", fg='red'))
        else:
            click.echo(click.style(f"Error: {response.status_code}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))

@cli.command()
def interactive():
    """Interactive mode for querying data"""
    click.echo(click.style("\n=== IoT Data Lake Interactive Mode ===\n", fg='cyan', bold=True))
    
    # Step 1: List available schemas
    try:
        response = requests.get(f"{API_BASE_URL}/profiles")
        if response.status_code != 200:
            click.echo(click.style("Error fetching profiles", fg='red'))
            return
        
        data = response.json()
        profile_ids = data['profile_ids']
        
        if not profile_ids:
            click.echo("No profiles available")
            return
        
        # Display profiles
        click.echo("Available Profiles:\n")
        for i, profile_id in enumerate(profile_ids, 1):
            click.echo(f"{i}. {profile_id}")
        
        # Step 2: User selects a profile
        selection = click.prompt('\nSelect a profile number', type=int)
        if selection < 1 or selection > len(profile_ids):
            click.echo(click.style("Invalid selection", fg='red'))
            return
        
        selected_profile = profile_ids[selection - 1]
        click.echo(f"\nSelected Profile: {click.style(selected_profile, fg='green')}")
        
        # Step 3: Show schema
        show_schema_option = click.confirm('\nShow schema for this profile?', default=True)
        if show_schema_option:
            response = requests.get(f"{API_BASE_URL}/schemas/{selected_profile}")
            if response.status_code == 200:
                schema_data = response.json()
                click.echo("\nSample Data Structure:")
                click.echo(json.dumps(schema_data['schema'].get('sample_data', {}), indent=2))
        
        # Step 4: Query data
        click.echo("\n" + "="*50)
        click.echo("Query Parameters:")
        
        use_time_range = click.confirm('Use time range filter?', default=False)
        start_time = None
        end_time = None
        
        if use_time_range:
            start_time = click.prompt('Start time (e.g., "1h", "1d", or ISO format)', default='1h')
            start_time = parse_time(start_time)
            end_time_input = click.prompt('End time (ISO format, or press Enter for now)', default='', show_default=False)
            if end_time_input:
                end_time = parse_time(end_time_input)
        
        limit = click.prompt('Maximum records', type=int, default=100)
        
        # Query data
        params = {'limit': limit}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        response = requests.get(f"{API_BASE_URL}/data/profile/{selected_profile}", params=params)
        
        if response.status_code == 200:
            result_data = response.json()
            records = result_data['data']
            
            click.echo(f"\n{click.style(f'Found {len(records)} records', fg='green', bold=True)}\n")
            
            if records:
                output_format = click.prompt('Output format', type=click.Choice(['table', 'json']), default='table')
                
                if output_format == 'json':
                    click.echo(json.dumps(records, indent=2))
                else:
                    display_data_table(records)
        else:
            click.echo(click.style(f"Error querying data: {response.status_code}", fg='red'))
            
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))


def parse_time(time_str: str) -> str:
    """
    Parse time string (relative or absolute) to ISO format
    
    Args:
        time_str: Time string (e.g., "1h", "1d", or ISO format)
        
    Returns:
        ISO format timestamp
    """
    if not time_str:
        return datetime.utcnow().isoformat()
    
    # Check if it's a relative time
    if time_str.endswith('h'):
        hours = int(time_str[:-1])
        dt = datetime.utcnow() - timedelta(hours=hours)
        return dt.isoformat()
    elif time_str.endswith('d'):
        days = int(time_str[:-1])
        dt = datetime.utcnow() - timedelta(days=days)
        return dt.isoformat()
    elif time_str.endswith('m'):
        minutes = int(time_str[:-1])
        dt = datetime.utcnow() - timedelta(minutes=minutes)
        return dt.isoformat()
    else:
        # Try to parse as ISO format
        try:
            dt = parser.parse(time_str)
            return dt.isoformat()
        except:
            return time_str


def display_trust_info(response_data: Dict[str, Any]):
    """
    Display trust and traceability information
    
    Args:
        response_data: API response containing trust_info and traceability
    """
    click.echo("\n" + "="*60)
    click.echo(click.style("🔐 TRUST & TRACEABILITY INFORMATION", fg='cyan', bold=True))
    click.echo("="*60)
    
    # Trust Information
    if 'trust_info' in response_data:
        trust_info = response_data['trust_info']
        click.echo(click.style("\n📊 Data Trust Statistics:", fg='yellow', bold=True))
        click.echo(f"  • Trusted Records: {trust_info.get('trusted_records', 0)}")
        click.echo(f"  • Signed Records: {trust_info.get('signed_records', 0)}")
        trust_pct = trust_info.get('trust_percentage', 0)
        
        # Color code trust percentage
        if trust_pct >= 90:
            color = 'green'
            status = '✓ Excellent'
        elif trust_pct >= 70:
            color = 'yellow'
            status = '⚠ Good'
        else:
            color = 'red'
            status = '✗ Low'
        
        click.echo(f"  • Trust Percentage: {click.style(f'{trust_pct:.1f}%', fg=color, bold=True)} {status}")
    
    # Traceability Information
    if 'traceability' in response_data:
        trace_info = response_data['traceability']
        click.echo(click.style("\n📋 Traceability:", fg='yellow', bold=True))
        click.echo(f"  • Consumer ID: {trace_info.get('consumer_id', 'N/A')}")
        click.echo(f"  • Access Logged: {click.style('✓ Yes', fg='green') if trace_info.get('access_logged') else '✗ No'}")
    
    click.echo("="*60 + "\n")


def display_data_table(records: List[Dict[str, Any]], show_trust: bool = False):
    """
    Display data records as a formatted table
    
    Args:
        records: List of data records
        show_trust: Whether to show trust indicators in the table
    """
    if not records:
        return
    
    # Prepare table data
    table_data = []
    headers = ['Sensor ID', 'Timestamp', 'Data']
    
    if show_trust:
        headers.extend(['Trusted', 'Signed', 'Owner'])
    
    for record in records:
        sensor_id = record.get('sensor_id', 'N/A')
        timestamp = record.get('timestamp', 'N/A')
        data = record.get('data', {})
        
        # Format data as string
        data_str = json.dumps(data, indent=2)
        if len(data_str) > 100:
            data_str = data_str[:100] + '...'
        
        row = [sensor_id, timestamp, data_str]
        
        if show_trust:
            trusted = '✓' if record.get('data_trusted', False) else '✗'
            signed = '✓' if record.get('data_signed', False) else '✗'
            owner = record.get('data_owner', 'N/A')
            row.extend([trusted, signed, owner])
        
        table_data.append(row)
    
    click.echo(tabulate(
        table_data,
        headers=headers,
        tablefmt='grid'
    ))


if __name__ == '__main__':
    cli()

# Made with Bob
