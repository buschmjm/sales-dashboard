import anvil.secrets
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.server
import requests
import time
from datetime import datetime, timedelta
import pytz
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

# Add these constants at the top with the other constants
SUPPORTED_PERIODS = ['D7', 'D30', 'D90', 'D180']
DEFAULT_PERIOD = 'D7'  # Use 7 days as default period

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

def get_today_messages_count(access_token, user_email):
    """Get count of today's messages for a specific user"""
    try:
        print(f"\nGetting message count for: {user_email}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "ConsistencyLevel": "eventual"
        }
        
        # Get user ID first
        search_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users?$select=id,mail&$filter=mail eq '{user_email}'"
        print(f"Searching for user ID with URL: {search_url}")
        
        search_response = requests.get(search_url, headers=headers)
        print(f"Search response status: {search_response.status_code}")
        
        if search_response.status_code != 200:
            print(f"User search failed: {search_response.text}")
            return None
            
        user_data = search_response.json().get("value", [])
        if not user_data:
            print(f"No Microsoft account found for {user_email}")
            return None
            
        user_id = user_data[0]["id"]
        print(f"Found user ID: {user_id}")
        
        # Get message counts for today
        cst = pytz.timezone('America/Chicago')
        today = datetime.now(cst).replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today.isoformat()
        
        # Build filter queries
        inbox_url = (f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/inbox/messages?"
                    f"$filter=receivedDateTime ge {today_str}&$count=true&$top=1")
        sent_url = (f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/sentitems/messages?"
                    f"$filter=sentDateTime ge {today_str}&$count=true&$top=1")
        
        # Add prefer header for count
        headers["Prefer"] = "outlook.timezone=\"Central Standard Time\""
        
        print("Fetching inbox count...")
        inbox_response = requests.get(inbox_url, headers=headers)
        print("Fetching sent items count...")
        sent_response = requests.get(sent_url, headers=headers)
        
        if inbox_response.status_code == 200 and sent_response.status_code == 200:
            inbox_data = inbox_response.json()
            sent_data = sent_response.json()
            
            inbox_count = inbox_data.get('@odata.count', 0)
            sent_count = sent_data.get('@odata.count', 0)
            
            return {
                "user": user_email,
                "inbox_count": inbox_count,
                "sent_count": sent_count
            }
        else:
            print(f"Failed to get counts. Inbox: {inbox_response.status_code}, Sent: {sent_response.status_code}")
            print(f"Inbox response: {inbox_response.text}")
            print(f"Sent response: {sent_response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting message counts for {user_email}: {str(e)}")
        print(f"Full error details: {repr(e)}")
        return None

@anvil.server.callable
def fetch_user_email_stats():
    """Fetch email statistics for all users"""
    try:
        print("\n=== Starting Email Stats Fetch ===")
        
        access_token = get_access_token()
        if not access_token:
            raise Exception("Failed to get access token")
            
        print("Access token obtained successfully")
        
        # Get all users that have an email field
        users = app_tables.users.search()
        valid_users = []
        
        for user in users:
            try:
                email = user.get('email', '')  # Use get() method with default value
                if email and isinstance(email, str):
                    valid_users.append({"email": email.strip().lower()})
            except Exception as e:
                print(f"Error accessing user data: {str(e)}")
                continue
        
        print(f"Found {len(valid_users)} valid users to process")
        
        results = []
        successful_fetches = 0

        for user in valid_users:
            try:
                email = user['email']
                print(f"\nProcessing user: {email}")
                
                user_stats = get_today_messages_count(access_token, email)
                if user_stats:
                    print(f"Got stats for {email}: {user_stats}")
                    results.append(user_stats)
                    successful_fetches += 1
                    
            except Exception as user_error:
                print(f"Error processing user {email}: {str(user_error)}")
                print(f"Full error details: {repr(user_error)}")
                continue
                
        print(f"\nSuccessfully processed {successful_fetches} users")
        
        if results:
            success = update_outlook_statistics_db(results)
            if not success:
                print("Warning: Database update returned False")
        
        return results
        
    except Exception as e:
        print(f"Error fetching email stats: {str(e)}")
        print(f"Full error details: {repr(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        return []

# Remove parse_csv_response function as it's no longer needed

