import anvil.server
import requests
import json
import base64
from anvil.tables import app_tables

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
    tokens = app_tables.tokens.search()
    token_row = None
    for t in tokens:
        token_row = t
        break
    if token_row:
        ACCESS_TOKEN = token_row['access_token']
        REFRESH_TOKEN = token_row['refresh_token']

def save_tokens(access_token, refresh_token):
    """Save ACCESS_TOKEN and REFRESH_TOKEN to the tokens table, replacing any existing rows."""
    # Clear existing rows
    for row in app_tables.tokens.search():
        row.delete()
    # Add the new tokens
    app_tables.tokens.add_row(access_token=access_token, refresh_token=refresh_token)


# ===============================================
# Utility Functions
# ===============================================
def encode_client_credentials(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

def get_authorization_url(state="12345"):
    scope = "call-control.v1.calls.control calls.v2.initiate"
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

# ===============================================
# Pre-Load Tokens from Provided Dictionary (Persistent Setup)
# ===============================================
# Use the provided tokens and store them persistently if not present
provided_access_token = "eyJraWQiOiI2MjAiLCJhbGciOiJSUzUxMiJ9.eyJzYyI6ImNhbGwtY29udHJvbC52MS5jYWxscy5jb250cm9sIGNhbGxzLnYyLmluaXRpYXRlIG1lc3NhZ2luZy52MS53cml0ZSBpZGVudGl0eTpzY2ltLm1lIGNhbGwtZXZlbnRzLnYxLmV2ZW50cy5yZWFkIG1lc3NhZ2luZy52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB2b2ljZW1haWwudjEubm90aWZpY2F0aW9ucy5tYW5hZ2UgcmVjb3JkaW5nLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIHN1cHBvcnQ6IHZvaWNlbWFpbC52MS52b2ljZW1haWxzLndyaXRlIGZheC52MS53cml0ZSB2b2ljZS1hZG1pbi52MS53cml0ZSBpZGVudGl0eTogd2VicnRjLnYxLnJlYWQgd2VicnRjLnYxLndyaXRlIGNvbGxhYjogdm9pY2UtYWRtaW4udjEucmVhZCBwcmVzZW5jZS52MS5yZWFkIHJlY29yZGluZy52MS5yZWFkIGNhbGwtZXZlbnRzLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIGlkZW50aXR5OnNjaW0ub3JnIHByZXNlbmNlLnYxLndyaXRlIGZheC52MS5yZWFkIGNhbGwtaGlzdG9yeS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBwcmVzZW5jZS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBtZXNzYWdpbmcudjEuc2VuZCBtZXNzYWdpbmcudjEucmVhZCBjci52MS5yZWFkIGZheC52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB1c2Vycy52MS5saW5lcy5yZWFkIHZvaWNlbWFpbC52MS52b2ljZW1haWxzLnJlYWQiLCJzdWIiOiIxOTIxNzAxNTU0NjE0MDIxMzk4IiwiYXVkIjoiMjA5M2ZjYjMtZGQzNS00MzIwLWI1YmYtMWU5MmU3ZWYwMDMyIiwib2duIjoicHdkIiwibHMiOiJhMjI0NzlmOC00MTRiLTRkYzYtOWIwNC1kNDhiY2MwNzlmN2QiLCJ0eXAiOiJhIiwiZXhwIjoxNzMzNzc5NDY2LCJpYXQiOjE3MzM3NzU4NjYsImp0aSI6ImNhZGNmODlkLTgwNjItNDAwYi1iNzViLTBjMWE4YWRjN2Q4OCIsImxvYSI6M30.P-bZsArlW6QWey1okPCzgjLZYBQM3ghzNMfGxMSFxEQv8tnq5gqOrn1DLZt5Pi-v46uqo9S-ax8mbAznM7Q3vM_DveU1JvuAIT34BYA9tsqrg7Jc-FrHyj6AE8XRnvJXKKHO45A5BG3EILakmeqcQUrMmpfhd-OYHjIPAmspW5LwKMwdV0lH98zlUmnEsENFlWh7WI8-JXYOpUav-e-F4ozd9zgzIr6MXPHgsliUpKKoeZ9SbaBunj4SU0sOYf47-vhv4fFdRnwRBbu1b8zl08EMtK_xGbdNBLmVCqp4OorBpGx7qswNRc1e22mK4tfsaZnGok1Pij4fFW62Fw1aEA"
provided_refresh_token = "eyJraWQiOiI2MjAiLCJhbGciOiJSUzUxMiJ9.eyJzYyI6ImNhbGwtY29udHJvbC52MS5jYWxscy5jb250cm9sIGNhbGxzLnYyLmluaXRpYXRlIG1lc3NhZ2luZy52MS53cml0ZSBpZGVudGl0eTpzY2ltLm1lIGNhbGwtZXZlbnRzLnYxLmV2ZW50cy5yZWFkIG1lc3NhZ2luZy52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB2b2ljZW1haWwudjEubm90aWZpY2F0aW9ucy5tYW5hZ2UgcmVjb3JkaW5nLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIHN1cHBvcnQ6IHZvaWNlbWFpbC52MS52b2ljZW1haWxzLndyaXRlIGZheC52MS53cml0ZSB2b2ljZS1hZG1pbi52MS53cml0ZSBpZGVudGl0eTogd2VicnRjLnYxLnJlYWQgd2VicnRjLnYxLndyaXRlIGNvbGxhYjogdm9pY2UtYWRtaW4udjEucmVhZCBwcmVzZW5jZS52MS5yZWFkIHJlY29yZGluZy52MS5yZWFkIGNhbGwtZXZlbnRzLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIGlkZW50aXR5OnNjaW0ub3JnIHByZXNlbmNlLnYxLndyaXRlIGZheC52MS5yZWFkIGNhbGwtaGlzdG9yeS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBwcmVzZW5jZS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBtZXNzYWdpbmcudjEuc2VuZCBtZXNzYWdpbmcudjEucmVhZCBjci52MS5yZWFkIGZheC52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB1c2Vycy52MS5saW5lcy5yZWFkIHZvaWNlbWFpbC52MS52b2ljZW1haWxzLnJlYWQiLCJzdWIiOiIxOTIxNzAxNTU0NjE0MDIxMzk4IiwiYXVkIjoiMjA5M2ZjYjMtZGQzNS00MzIwLWI1YmYtMWU5MmU3ZWYwMDMyIiwib2duIjoicHdkIiwidHlwIjoiciIsImV4cCI6MTczNjM2Nzg2NiwiaWF0IjoxNzMzNzc1ODY2LCJqdGkiOiI1MDBhYWMwYy0zY2FkLTQ5NWYtYTJmMS0zZWFhNWFhZWFmYjAiLCJsb2EiOjN9.1F04PPQEGDQG9ufoaFRknXxyI_29-5__WXG-lENrY03HwqlS7Nj_9zgLdQF4RhuMr4nUn7pvkKM0rDOp_hlcYpCbclT0FfJZMPakWF5VdRWtHg2zjw5u2fLQu2QzL8p4P3Fz89UeuEeXSAC5TbIugaKkZR8-K_SgsquMX6wWwaWutPE-u6Q_Y_0g5FYlcoz9erQuAWCbq-51zWWLqijrtCT2pPXO1ilskq8wg9lgacohL9T5I5AV0NXGvma0uSSrsM8wAZg2xK-WyPhf89vRqaPaVRGdVfVDOV2xkldzeJPvQEKbQ6u6u25--6G2mrAV7HaiZTV-gIbovozZctMGNw"

# Load existing tokens, or if none exist, save the provided ones
load_tokens()
if ACCESS_TOKEN is None or REFRESH_TOKEN is None:
    ACCESS_TOKEN = provided_access_token
    REFRESH_TOKEN = provided_refresh_token
    save_tokens(ACCESS_TOKEN, REFRESH_TOKEN)

# ===============================================
# Fetch Call Reports
# ===============================================
@anvil.server.callable
def fetch_call_reports_requests():
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        raise Exception("Access token not available. Complete the authorization flow first.")

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{CALL_REPORTS_URL}?organizationId=0127d974-f9f3-0704-2dee-000100422009",
        headers=headers
    )

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
