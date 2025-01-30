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

# Load any previously saved tokens
load_tokens()

def initialize_auth():
    """Initialize authorization using Personal Access Key"""
    global ACCESS_TOKEN
    
    try:
        # Get credentials from database
        creds = get_credentials()
        if not creds:
            print("No credentials found in database")
            return False
            
        # Use Personal Access Key directly
        if not creds.get('personal_key'):
            print("No Personal Access Key found in credentials")
            return False
            
        print("\nInitializing with Personal Access Key...")
        ACCESS_TOKEN = creds['personal_key']
        
        # Verify the token works
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Accept": "application/json"
        }
        
        # Test the token with a simple API call
        now = datetime.utcnow()
        test_url = f"{CALL_REPORTS_URL}?startTime={now.isoformat()}Z&endTime={now.isoformat()}Z"
        
        print("Testing Personal Access Key...")
        response = requests.get(test_url, headers=headers)
        
        if response.status_code in (200, 404):  # Both are valid responses
            print("Personal Access Key verified successfully")
            save_tokens(ACCESS_TOKEN, None)  # No refresh token needed with PAK
            return True
        else:
            print(f"Personal Access Key verification failed. Status: {response.status_code}")
            print(f"Error Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during authorization initialization: {str(e)}")
        return False

# Remove or comment out unused OAuth-related functions
# def refresh_access_token():
# def handle_oauth_callback():

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

@anvil.server.callable
def initialize_goto_credentials(client_id, client_secret, personal_access_key):
    """Initialize GoTo credentials in the tokens table"""
    try:
        # Clear existing tokens
        for row in app_tables.tokens.search():
            row.delete()
            
        # Add new credentials
        app_tables.tokens.add_row(
            **{
                'Client ID': client_id,
                'Secret': client_secret,
                'Personal Access Key': personal_access_key,
                'access_token': personal_access_key  # Use PAK as initial access token
            }
        )
        
        # Test the credentials
        if initialize_auth():
            print("Successfully initialized GoTo credentials")
            return True
        else:
            print("Credentials verification failed")
            return False
            
    except Exception as e:
        print(f"Error initializing credentials: {e}")
        return False

