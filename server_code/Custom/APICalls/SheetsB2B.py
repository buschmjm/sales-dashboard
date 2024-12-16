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
    
    print("Fetching data from Google Sheets...")  # Debug log
    
    # Update this URL with your actual deployed Apps Script web app URL
    url = "https://script.google.com/macros/s/AKfycbzrm6ttNyYRxfibYUHYExxlWruT33m1gXdDRZFo4hLFap0zkmhutKKkHdpQNW27GdS4Yw/exec"
    
    # Query parameters - always include the key and sheet name
    params = {
        "key": api_key,
        "sheet": "Form Responses 1"  # Explicitly specify sheet name
    }
    
    # Add filters if provided
    if sales_rep:
        params["Sales Rep"] = sales_rep
    if complete is not None:
        params["Complete"] = str(complete).lower()
    
    try:
        print(f"Making API request with params: {params}")  # Debug log
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"Received {len(data)} records from sheet")  # Debug log
        return data
        
    except Exception as e:
        print(f"Error fetching sheet data: {e}")
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
    try:
        # Fetch the data from Google Sheets
        sheet_data = fetch_google_sheet_data()
        print(f"Processing {len(sheet_data)} records from sheet")
        
        new_records_count = 0
        
        # Process each row
        for row in sheet_data:
            try:
                timestamp_str = row.get('Timestamp')
                if not timestamp_str:
                    print(f"Skipping row - no timestamp: {row}")
                    continue
                    
                timestamp = parse_timestamp(timestamp_str)
                if not timestamp:
                    continue
                
                sales_rep = row.get('Sales Rep')
                if not sales_rep:
                    print(f"Skipping row - no sales rep: {row}")
                    continue
                
                # Check for existing record
                existing = app_tables.b2b.get(
                    timestamp=timestamp,
                    sales_rep=sales_rep
                )
                
                if existing:
                    print(f"Record exists for {sales_rep} at {timestamp}")
                    continue
                
                # Process marketing type
                marketing_type = row.get('C1', '').strip().lower()
                print(f"Processing marketing type: {marketing_type}")
                
                # Add new record
                app_tables.b2b.add_row(
                    timestamp=timestamp,
                    sales_rep=sales_rep,
                    complete=bool(row.get('Complete', False)),  # Ensure boolean
                    email='email' in marketing_type,
                    flyers='flyer' in marketing_type,
                    business_cards='business card' in marketing_type
                )
                
                new_records_count += 1
                print(f"Added new record for {sales_rep}")
                
            except Exception as row_error:
                print(f"Error processing row: {row_error}")
                continue
        
        print(f"Import complete. Added {new_records_count} new records")
        return new_records_count
        
    except Exception as e:
        print(f"Error in process_and_store_sheet_data: {e}")
        return 0
