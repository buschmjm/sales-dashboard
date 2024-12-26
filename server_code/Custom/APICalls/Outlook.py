import anvil.secrets
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server
import requests
import time
from datetime import datetime, timedelta
import pytz
import csv
from io import StringIO
from ..DataAggregation.Email import update_outlook_statistics_db

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Define Microsoft Graph API base URL
MICROSOFT_GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"

# Fetch API credentials from Anvil secrets
CLIENT_ID = anvil.secrets.get_secret("ms_client_id")
CLIENT_SECRET = anvil.secrets.get_secret("ms_client_secret")
TENANT_ID = anvil.secrets.get_secret("ms_tenant_id")

# Cache for access token
_access_token_cache = {
    "token": None,
    "expires_at": 0
}

def get_access_token():
    """Fetch an access token from Microsoft OAuth endpoint, with caching."""
    global _access_token_cache

    # Check if token is still valid
    if time.time() < _access_token_cache["expires_at"]:
        return _access_token_cache["token"]

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()

    token_data = response.json()
    _access_token_cache["token"] = token_data["access_token"]
    _access_token_cache["expires_at"] = time.time() + token_data["expires_in"] - 60  # Subtract 1 min buffer

    return _access_token_cache["token"]

@anvil.server.callable
def fetch_user_email_stats():
    """Fetch email activity reports using Microsoft Graph Reports API."""
    try:
        print("\n=== Starting Email Stats Fetch ===")
        
        access_token = get_access_token()
        if not access_token:
            raise Exception("Failed to get access token")
            
        print("Access token obtained successfully")
        
        # Use the reports endpoint to get email activity
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # Get today's email activity report (D1 for daily)
        url = f"{MICROSOFT_GRAPH_API_BASE_URL}/reports/getEmailActivityUserDetail(period='D1')"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch email stats: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
        # Parse CSV response
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        results = []
        for row in reader:
            try:
                # Extract relevant fields from the report
                user_stats = {
                    "user": row['User Principal Name'],
                    "inbox_count": int(row.get('Receive Count', 0)),
                    "sent_count": int(row.get('Send Count', 0))
                }
                results.append(user_stats)
                print(f"Processed stats for {user_stats['user']}")
                
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue
        
        if results:
            print(f"\nProcessed {len(results)} user statistics")
            success = update_outlook_statistics_db(results)
            if not success:
                print("Warning: Database update returned False")
            return results
            
        print("No results found in the report")
        return []
        
    except Exception as e:
        print(f"Error fetching email stats: {str(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        return []

# Remove fetch_single_user_stats as it's no longer needed

