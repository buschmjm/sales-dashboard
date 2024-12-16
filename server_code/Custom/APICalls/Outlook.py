import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import time
from datetime import datetime, timedelta
import pytz
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
    """Optimized email stats fetching with parallel processing where possible."""
    try:
        access_token = get_access_token()
        if not access_token:
            raise Exception("Failed to get access token")
            
        print("Starting email statistics fetch...")  # Debug log
        
        # Get all app users in one query
        users = list(app_tables.users.search())
        print(f"Found {len(users)} users to process")  # Debug log
        
        results = []
        successful_fetches = 0

        for user in users:
            try:
                email = user.get('email')
                if not email:
                    continue

                print(f"Processing user: {email}")  # Debug log
                
                # Update stats for this user
                user_stats = fetch_single_user_stats(access_token, user)
                if user_stats:
                    results.append(user_stats)
                    successful_fetches += 1
                    
            except Exception as user_error:
                print(f"Error processing user {user.get('email')}: {user_error}")
                continue

        print(f"Successfully processed {successful_fetches} users")  # Debug log
        
        if results:
            success = update_outlook_statistics_db(results)
            if not success:
                raise Exception("Failed to update database")
            return results
        return []

    except Exception as e:
        print(f"Error in fetch_user_email_stats: {str(e)}")
        return []

def fetch_single_user_stats(access_token, user):
    """Helper function to fetch stats for a single user"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": "outlook.timezone=\"Central Standard Time\"",
        "ConsistencyLevel": "eventual"
    }
    
    # Rest of the existing single user fetch code...

