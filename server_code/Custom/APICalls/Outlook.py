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
    """Fetch email stats (inbox and sent count) for all app users."""
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Get all app users
    app_users = app_tables.users.search()
    results = []

    # Get today's date in CST (America/Chicago timezone)
    cst_tz = pytz.timezone("America/Chicago")
    now = datetime.now(cst_tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Format date for Microsoft Graph API
    today_iso = today_start.isoformat() + 'Z'
    
    print(f"Fetching email stats for date: {today_iso}")

    for user in app_users:
        email = user["email"]
        if not email:
            continue

        try:
            # Search for user in Microsoft Graph
            search_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users?$filter=mail eq '{email}' or userPrincipalName eq '{email}'"
            search_response = requests.get(search_url, headers=headers)
            search_response.raise_for_status()

            search_results = search_response.json().get("value", [])
            if not search_results:
                print(f"No Outlook user found for email: {email}")
                continue

            user_id = search_results[0]["id"]

            # Get inbox message count for today
            inbox_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/Inbox/messages?$count=true&$filter=receivedDateTime ge {today_iso}"
            inbox_response = requests.get(inbox_url, headers={"Authorization": f"Bearer {access_token}", "Prefer": "outlook.timezone=\"Central Standard Time\""})
            inbox_response.raise_for_status()

            inbox_count = inbox_response.json().get("@odata.count", 0)

            # Get sent message count for today
            sent_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/SentItems/messages?$count=true&$filter=sentDateTime ge {today_iso}"
            sent_response = requests.get(sent_url, headers={"Authorization": f"Bearer {access_token}", "Prefer": "outlook.timezone=\"Central Standard Time\""})
            sent_response.raise_for_status()

            sent_count = sent_response.json().get("@odata.count", 0)

            print(f"Stats for {email}: inbox={inbox_count}, sent={sent_count}")

            # Append results
            results.append({
                "user": email,
                "inbox_count": inbox_count,
                "sent_count": sent_count
            })

        except Exception as e:
            print(f"Error fetching email stats for {email}: {e}")

    # Update the database with the collected statistics
    if results:
        print(f"Updating database with {len(results)} records")
        update_outlook_statistics_db(results)
    else:
        print("No email statistics to update")
    
    return results

