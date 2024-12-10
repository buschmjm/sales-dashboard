import anvil.server
import requests
import json
import base64
from anvil.tables import app_tables
from datetime import datetime, timedelta

# ===============================================
# Configuration
# ===============================================
CLIENT_ID = "2093fcb3-dd35-4320-b5bf-1e92e7ef0032"
CLIENT_SECRET = "nkWiybVLmqvpVvS7jQRMaF5N"
REDIRECT_URI = "http://localhost:8000/callback"
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
        # Clear existing rows
        for row in app_tables.tokens.search():
            row.delete()
        # Add the new tokens
        app_tables.tokens.add_row(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        print(f"Error saving tokens: {e}")

# ===============================================
# Utility Functions
# ===============================================
def encode_client_credentials(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

def get_authorization_url(state="12345"):
    scope = "call-control.v1.calls.control calls.v2.initiate cr.v1.read"
    auth_url = (
        f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}&state={state}"
    )
    return auth_url

def exchange_authorization_code(auth_code):
    global ACCESS_TOKEN, REFRESH_TOKEN

    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID
    }
    headers = {
        "Authorization": f"Basic {encode_client_credentials(CLIENT_ID, CLIENT_SECRET)}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        ACCESS_TOKEN = tokens["access_token"]
        REFRESH_TOKEN = tokens.get("refresh_token")
        save_tokens(ACCESS_TOKEN, REFRESH_TOKEN)
        print("Tokens exchanged and saved successfully.")
    else:
        raise Exception(f"Failed to exchange authorization code: {response.text}")

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

# ===============================================
# Fetch Call Reports for Yesterday
# ===============================================
@anvil.server.callable
def fetch_call_reports_requests():
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        raise Exception("Access token not available. Complete the authorization flow first.")

    # Calculate startTime as the start of today and endTime as the current time in UTC
    now = datetime.utcnow()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = start_of_today.isoformat() + "Z"  # Start of today
    end_time = now.isoformat() + "Z"  # Current time

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    # Construct the API URL with the updated time range
    url = (
        f"{CALL_REPORTS_URL}"
        f"?startTime={start_time}"
        f"&endTime={end_time}"
    )

    # Make the API request
    response = requests.get(url, headers=headers)

    # Handle authentication errors
    if response.status_code == 401:
        print("Access token expired. Attempting to refresh...")
        refresh_access_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        response = requests.get(url, headers=headers)

    # Handle response
    if response.status_code == 200:
        data = response.json()
        print("Fetched data:", json.dumps(data, indent=4))  # Pretty-print JSON data to the console
        return data
    elif response.status_code == 404:
        print("No data found for the specified time frame.")
        return {"message": "No data found for the specified time frame."}
    else:
        raise Exception(f"Failed to fetch call data: {response.status_code} - {response.text}")
