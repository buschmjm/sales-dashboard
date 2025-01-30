import anvil.secrets
import anvil.server
import requests
import json
import base64
from anvil.tables import app_tables
from datetime import datetime, timedelta

# ===============================================
# Configuration
# ===============================================
def get_credentials():
    """Get GoTo credentials from database"""
    try:
        creds = app_tables.tokens.search()
        for row in creds:
            return {
                'client_id': row.get('Client ID', ''),
                'client_secret': row.get('Secret', ''),
                'access_token': row.get('access_token', ''),
                'personal_key': row.get('Personal Access Key', '')
            }
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

# Remove hardcoded credentials
CLIENT_ID = None
CLIENT_SECRET = None
ACCESS_TOKEN = None
REFRESH_TOKEN = None

TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
AUTH_URL = "https://authentication.logmeininc.com/oauth/authorize"
CALL_REPORTS_URL = "https://api.goto.com/call-reports/v1/reports/user-activity"

# Global variables for tokens
ACCESS_TOKEN = None
REFRESH_TOKEN = None

# ===============================================
# Persistent Token Storage/Loading
# ===============================================
def load_tokens():
    """Load ACCESS_TOKEN and REFRESH_TOKEN from the tokens table."""
    global ACCESS_TOKEN, REFRESH_TOKEN
    try:
        tokens = app_tables.tokens.search()
        token_row = None
        for t in tokens:
            token_row = t
            break
        if token_row:
            ACCESS_TOKEN = token_row['access_token']
            REFRESH_TOKEN = token_row['refresh_token']
    except Exception as e:
        print(f"Error loading tokens: {e}")

def save_tokens(access_token, refresh_token):
    """Save ACCESS_TOKEN and REFRESH_TOKEN to the tokens table, replacing any existing rows."""
    try:
        for row in app_tables.tokens.search():
            row.delete()
        app_tables.tokens.add_row(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        print(f"Error saving tokens: {e}")

# ===============================================
# Utility Functions
# ===============================================
def encode_client_credentials(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

def refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN

    if not REFRESH_TOKEN:
        raise Exception("No refresh token available. Start the authorization flow again.")

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    headers = {
        "Authorization": f"Basic {encode_client_credentials(CLIENT_ID, CLIENT_SECRET)}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        ACCESS_TOKEN = tokens["access_token"]
        REFRESH_TOKEN = tokens.get("refresh_token", REFRESH_TOKEN)
        save_tokens(ACCESS_TOKEN, REFRESH_TOKEN)
        print("Access token refreshed and saved successfully.")
    else:
        raise Exception(f"Failed to refresh access token: {response.text}")

# Load any previously saved tokens
load_tokens()

def initialize_auth():
    """Initialize authorization using stored credentials"""
    global ACCESS_TOKEN
    
    try:
        # Get credentials from database
        creds = get_credentials()
        if not creds:
            print("No credentials found in database")
            return False
            
        # Use personal access key if available
        if creds['personal_key']:
            ACCESS_TOKEN = creds['personal_key']
            save_tokens(ACCESS_TOKEN, None)
            print("Using personal access key for authentication")
            return True
            
        # Otherwise try client credentials
        auth_string = f"{creds['client_id']}:{creds['client_secret']}"
        auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        payload = {
            "grant_type": "client_credentials",
            "scope": "call-reports:read"
        }
        
        print("\nAttempting authorization with client credentials...")
        response = requests.post(
            TOKEN_URL, 
            data=payload,
            headers=headers,
            verify=True
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            ACCESS_TOKEN = tokens["access_token"]
            save_tokens(ACCESS_TOKEN, None)
            print("Successfully initialized with client credentials")
            return True
        else:
            print(f"Authorization failed. Status: {response.status_code}")
            print(f"Error Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during authorization initialization: {str(e)}")
        return False

# Add a function to handle the OAuth callback
@anvil.server.callable
def handle_oauth_callback(code):
    """Handle the OAuth callback and store the authorization code"""
    try:
        anvil.secrets.set_secret('refresh_token', code)
        return initialize_auth()
    except Exception as e:
        print(f"Error handling OAuth callback: {str(e)}")
        return False

# ===============================================
# Update Data Table with API Data
# ===============================================
def update_call_statistics(data):
    today_date = datetime.utcnow().date()

    for item in data.get("items", []):
        user_id = item["userId"]
        user_name = item["userName"]
        data_values = item["dataValues"]

        # Check if a record exists for this user ID and today's date
        existing_row = app_tables.call_statistics.get(
            userId=user_id, reportDate=today_date
        )

        if existing_row:
            # Update the existing record
            existing_row.update(
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
            )
        else:
            # Add a new record
            app_tables.call_statistics.add_row(
                userId=user_id,
                userName=user_name,
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
                reportDate=today_date,
            )

# ===============================================
# Fetch Call Reports (Manual Trigger)
# ===============================================
@anvil.server.callable
def fetch_call_reports():
    global ACCESS_TOKEN
    
    if not ACCESS_TOKEN:
        if not initialize_auth():
            raise Exception("Failed to initialize authorization. Please check your credentials.")
    
    # Calculate startTime as the start of today and endTime as the current time in UTC
    now = datetime.utcnow()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = start_of_today.isoformat() + "Z"
    end_time = now.isoformat() + "Z"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    url = f"{CALL_REPORTS_URL}?startTime={start_time}&endTime={end_time}"

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        print("Access token expired. Attempting to refresh...")
        refresh_access_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        update_call_statistics(data)
        return {"message": "Data refreshed successfully."}
    elif response.status_code == 404:
        return {"message": "No data found for the specified time frame."}
    else:
        raise Exception(f"Failed to fetch call data: {response.status_code} - {response.text}")

