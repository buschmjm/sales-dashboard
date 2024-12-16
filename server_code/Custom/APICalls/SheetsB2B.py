import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests

def fetch_google_sheet_data(sales_rep=None, complete=None):
    # Get the secret key from Anvil's Secrets Service
    api_key = anvil.secrets.get_secret("5Up3rS3cr3t_K3y!2024#@Xz")
    
    # API URL
    url = "https://script.google.com/macros/s/AKfycbzrm6ttNyYRxfibYUHYExxlWruT33m1gXdDRZFo4hLFap0zkmhutKKkHdpQNW27GdS4Yw/exec"
    
    # Query parameters
    params = {
        "key": api_key
    }
    
    # Add filters if provided
    if sales_rep:
        params["Sales Rep"] = sales_rep
    if complete:
        params["Complete"] = complete
    
    # Make the GET request
    response = requests.get(url, params=params)
    
    # Check for errors
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")
    
    # Return the parsed JSON response
    return response.json()

@anvil.server.callable
def process_and_store_sheet_data():
    # Fetch the data from Google Sheets
    sheet_data = fetch_google_sheet_data()
    
    # Initialize counter for new records
    new_records_count = 0
    
    # Reverse the data to start from the bottom
    for row in reversed(sheet_data):
        # Check if this record already exists
        existing_record = app_tables.b2b_data.get(
            Timestamp=row.get('Timestamp'),
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
            Timestamp=row.get('Timestamp'),
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
