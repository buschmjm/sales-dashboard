import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
from datetime import datetime, time

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!") 
#   return 42

@anvil.server.callable
def get_b2b_stats(start_date, end_date, metric):
    """Get B2B statistics from Google Sheet for the given date range and metric"""
    try:
        print(f"Querying B2B stats for {metric} from {start_date} to {end_date}")
        
        # Convert dates to datetime for comparison
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        
        # Call the Google Sheet API endpoint
        api_key = anvil.secrets.get_secret("b2b_sheets_secret")
        url = "https://script.google.com/macros/s/AKfycbzrm6ttNyYRxfibYUHYExxlWruT33m1gXdDRZFo4hLFap0zkmhutKKkHdpQNW27GdS4Yw/exec"
        
        response = requests.get(
            url,
            params={"key": api_key},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {"users": ["No Data"], "metrics": {}}
            
        # Process the sheet data
        sheet_data = response.json()
        sales_reps = set()
        metric_counts = {}
        
        skipped_rows = 0
        for row in sheet_data:
            try:
                # Validate timestamp exists and is not empty
                timestamp_str = row.get('Timestamp', '').strip()
                if not timestamp_str:
                    skipped_rows += 1
                    continue
                
                try:
                    timestamp = datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    # Try alternate format if first fails
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"Invalid timestamp format: {timestamp_str}")
                        skipped_rows += 1
                        continue
                
                # Check if within date range
                if not (start_dt <= timestamp <= end_dt):
                    continue
                    
                # Get sales rep
                sales_rep = row.get('Sales Rep', '').strip()
                if not sales_rep:
                    skipped_rows += 1
                    continue
                    
                # Check promotional material type
                promo_material = row.get('Promotional Material the customer would like?', '').strip()
                if metric.lower() in promo_material.lower():
                    sales_reps.add(sales_rep)
                    metric_counts[sales_rep] = metric_counts.get(sales_rep, 0) + 1
                    
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                print(f"Problematic row data: {row}")
                skipped_rows += 1
                continue
        
        print(f"Found {len(sales_reps)} sales reps with {metric} data")
        print(f"Skipped {skipped_rows} invalid rows")
        print(f"Counts: {metric_counts}")
        
        return {
            "users": sorted(list(sales_reps)) or ["No Data"],
            "metrics": metric_counts
        }
        
    except Exception as e:
        print(f"Error in get_b2b_stats: {e}")
        return {"users": ["No Data"], "metrics": {}}
