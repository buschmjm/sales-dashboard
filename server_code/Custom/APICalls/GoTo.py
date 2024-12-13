import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.server
import anvil.http
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

    response = anvil.http.request(TOKEN_URL, method="POST", headers=headers, data=payload, json=True)
    if response.status_code == 200:
        tokens = response.get_bytes()
        ACCESS_TOKEN = tokens["access_token"]
        REFRESH_TOKEN = tokens.get("refresh_token", REFRESH_TOKEN)
        save_tokens(ACCESS_TOKEN, REFRESH_TOKEN)
        print("Access token refreshed and saved successfully.")
    else:
        raise Exception(f"Failed to refresh access token: {response.content}")

# Load any previously saved tokens
load_tokens()

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
        raise Exception("Access token not available. Complete the authorization flow first.")

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

    response = anvil.http.request(url, method="GET", headers=headers, json=True)

    if response.status_code == 401:
        print("Access token expired. Attempting to refresh...")
        refresh_access_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        response = anvil.http.request(url, method="GET", headers=headers, json=True)

    if response.status_code == 200:
        data = response.get_bytes()
        update_call_statistics(data)
        return {"message": "Data refreshed successfully."}
    elif response.status_code == 404:
        return {"message": "No data found for the specified time frame."}
    else:
        raise Exception(f"Failed to fetch call data: {response.status_code} - {response.content}")

# ===============================================
# Fetch Call Reports (Scheduled Task)
# ===============================================
@anvil.server.background_task
def fetch_call_reports_scheduled():
    fetch_call_reports()
