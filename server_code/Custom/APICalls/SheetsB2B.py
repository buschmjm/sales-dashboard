import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import json
from datetime import datetime

def fetch_google_sheet_data(sales_rep=None, complete=None):
    # Get the secret key from Anvil's Secrets Service
    api_key = anvil.secrets.get_secret("5Up3rS3cr3t_K3y!2024#@Xz")
    
    # Update this URL with your actual deployed Apps Script web app URL
    url = "https://script.google.com/macros/s/YOUR_ACTUAL_DEPLOYMENT_ID/exec"
    
    # Query parameters - always include the key
    params = {
        "key": api_key
    }
    
    # Add filters if provided - match exact parameter names from Apps Script
    if sales_rep:
        params["Sales Rep"] = sales_rep
    if complete is not None:  # Changed to handle boolean values
        params["Complete"] = str(complete).lower()
    
    try:
        # Make the GET request
        response = requests.get(url, params=params, timeout=30)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Verify we got JSON response
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type.lower():
            raise ValueError(f"Expected JSON response, got {content_type}")
        
        # Parse and validate the response
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Expected JSON array in response")
            
        return data
        
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
        raise Exception(f"Failed to fetch sheet data: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {str(e)}")
        raise Exception("Invalid response format from API")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

def parse_timestamp(timestamp_str):
    """Parse timestamp string from Google Sheets to datetime object"""
    try:
        # Assuming format like "9/11/2024 10:06:35"
        return datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
    except ValueError as e:
        print(f"Error parsing timestamp {timestamp_str}: {e}")
        return None

@anvil.server.callable
def process_and_store_sheet_data():
    # Fetch the data from Google Sheets
    sheet_data = fetch_google_sheet_data()
    
    # Initialize counter for new records
    new_records_count = 0
    
    # Reverse the data to start from the bottom
    for row in reversed(sheet_data):
        # Parse timestamp
        timestamp = parse_timestamp(row.get('Timestamp'))
        if not timestamp:
            continue
            
        # Check if this record already exists
        existing_record = app_tables.b2b_data.get(
            Timestamp=timestamp,
            Sales_Rep=row.get('Sales Rep')
        )
        
        # If record exists, stop processing
        if existing_record:
            if new_records_count == 0:
                print("No new records found")
            else:
                print(f"Import complete. Added {new_records_count} new records")
            return new_records_count
        
        # Process new record
        marketing_type = row.get('C1', '').strip()
        marketing_fields = {
            'Email': False,
            'Flyers': False,
            'Business Cards': False
        }
        
        for field in marketing_fields:
            if field.lower() in marketing_type.lower():
                marketing_fields[field] = True
        
        # Add new record to database
        app_tables.b2b_data.add_row(
            Timestamp=timestamp,  # Now using parsed datetime object
            Sales_Rep=row.get('Sales Rep'),
            Complete=row.get('Complete'),
            Email=marketing_fields['Email'],
            Flyers=marketing_fields['Flyers'],
            Business_Cards=marketing_fields['Business Cards']
        )
        
        new_records_count += 1
    
    # If we processed all records without finding duplicates
    print(f"Import complete. Added {new_records_count} new records")
    return new_records_count
