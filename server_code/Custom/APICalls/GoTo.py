import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import json
import time

# Configuration (Hardcoded credentials)
CLIENT_ID = "2093fcb3-dd35-4320-b5bf-1e92e7ef0032"
CLIENT_SECRET = "tEJzrrwv8SMVNBEH6OCTSZWg"
TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
CALL_REPORTS_URL = "https://api.goto.com/call-reports/v1/reports/user-activity"

# Token variables
ACCESS_TOKEN = None
REFRESH_TOKEN = None

# Function to initialize and fetch the access and refresh tokens
def initialize_tokens():
    global ACCESS_TOKEN, REFRESH_TOKEN

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print("Initializing tokens...")  # Debugging log
    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        print("Initialization response status:", response.status_code)  # Debugging log
        print("Initialization response body:", response.text)  # Debugging log

        if response.status_code == 200:
            tokens = response.json()
            ACCESS_TOKEN = tokens["access_token"]
            REFRESH_TOKEN = tokens.get("refresh_token", None)  # May not be provided for client_credentials
            print("Tokens initialized successfully.")
        else:
            raise Exception(f"Failed to initialize tokens: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print("Network error during token initialization:", e)
        raise Exception("Network error while initializing tokens.") from e

# Function to refresh the access token
def refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN

    if not REFRESH_TOKEN:
        raise Exception("Refresh token not available. Please reinitialize tokens.")

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print("Attempting to refresh access token...")  # Debugging log
    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        print("Token refresh response status:", response.status_code)  # Debugging log
        print("Token refresh response body:", response.text)  # Debugging log

        if response.status_code == 200:
            tokens = response.json()
            ACCESS_TOKEN = tokens["access_token"]
            REFRESH_TOKEN = tokens.get("refresh_token", REFRESH_TOKEN)
            print("Access token refreshed successfully.")
        else:
            raise Exception(f"Failed to refresh access token: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print("Network error during token refresh:", e)
        raise Exception("Network error while refreshing token.") from e

# Fetch call data using requests
@anvil.server.callable
def fetch_call_reports_requests():
    global ACCESS_TOKEN

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    try:
        print("Fetching call reports...")  # Debugging log
        response = requests.get(
            f"{CALL_REPORTS_URL}?organizationId=0127d974-f9f3-0704-2dee-000100422009",
            headers=headers
        )
        print("Call reports response status:", response.status_code)  # Debugging log

        if response.status_code == 401:
            print("Access token expired. Attempting to refresh...")
            refresh_access_token()
            headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
            response = requests.get(
                f"{CALL_REPORTS_URL}?organizationId=0127d974-f9f3-0704-2dee-000100422009",
                headers=headers
            )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch call data: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print("Network error during call report fetch:", e)
        raise Exception("Network error while fetching call reports.") from e

# Retry logic for network errors
def safe_request(func, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

# Test callable for debugging
@anvil.server.callable
def test_token_refresh():
    print("Testing token refresh...")
    try:
        refresh_access_token()
        return "Token refresh successful."
    except Exception as e:
        return f"Token refresh failed: {e}"

# Example callable function
@anvil.server.callable
def say_hello(name):
    print(f"Hello, {name}!")
    return 42

# Initialize tokens when the app starts
initialize_tokens()
