import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import time

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
def get_email_stats():
    """Fetch the number of emails sent and received for each user."""
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "ConsistencyLevel": "eventual"
    }

    users_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users"
    response = requests.get(users_url, headers=headers)
    response.raise_for_status()

    users = response.json()["value"]
    email_stats = []

    for user in users:
        user_id = user["id"]
        display_name = user["displayName"]

        try:
            # Fetch Inbox message count
            inbox_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/Inbox/messages"
            inbox_response = requests.get(inbox_url, headers=headers, params={"$top": 1, "$count": "true"})
            inbox_response.raise_for_status()
            emails_received_count = inbox_response.json().get("@odata.count", "Error")
        except Exception as e:
            print(f"Inbox fetch failed for user {display_name}: {e}")
            emails_received_count = "Error"

        try:
            # Fetch SentItems message count
            sent_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/SentItems/messages"
            sent_response = requests.get(sent_url, headers=headers, params={"$top": 1, "$count": "true"})
            sent_response.raise_for_status()
            emails_sent_count = sent_response.json().get("@odata.count", "Error")
        except Exception as e:
            print(f"SentItems fetch failed for user {display_name}: {e}")
            emails_sent_count = "Error"

        email_stats.append({
            "user": display_name,
            "emails_sent": emails_sent_count,
            "emails_received": emails_received_count
        })

    return email_stats

@anvil.server.callable
def fetch_email_activity_user_detail(period="D30"):
    """Fetch detailed email activity for users over a specified period."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"{MICROSOFT_GRAPH_API_BASE_URL}/reports/getEmailActivityUserDetail(period='{period}')"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if response.status_code == 302:
        print("Redirected to download URL. Parsing report not implemented as per requirement.")
    else:
        raise Exception("Failed to fetch email activity user detail report.")

@anvil.server.callable
def fetch_email_activity_counts(period="D30"):
    """Fetch aggregated email activity counts for the organization."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    url = f"{MICROSOFT_GRAPH_API_BASE_URL}/reports/getEmailActivityCounts(period='{period}')"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if response.status_code == 302:
        print("Redirected to download URL. Parsing report not implemented as per requirement.")
    else:
        raise Exception("Failed to fetch email activity counts report.")
