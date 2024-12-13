import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.http
import time

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

    response = anvil.http.request(token_url, method="POST", headers=headers, data=data, json=True)
    token_data = response.get_bytes()
    _access_token_cache["token"] = token_data["access_token"]
    _access_token_cache["expires_at"] = time.time() + token_data["expires_in"] - 60  # Subtract 1 min buffer

    return _access_token_cache["token"]

def fetch_user_stats(email, headers, today):
    """Fetch inbox and sent message counts for a specific email."""
    try:
        # Search for user in Microsoft Graph
        search_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users?$filter=mail eq '{email}' or userPrincipalName eq '{email}'"
        search_response = anvil.http.request(search_url, method="GET", headers=headers, json=True)
        search_results = search_response.get_bytes().get("value", [])
        if not search_results:
            print(f"No Outlook user found for email: {email}")
            return {"user": email, "inbox_count": 0, "sent_count": 0}

        user_id = search_results[0]["id"]

        # Get inbox message count for today
        inbox_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/Inbox/messages?$count=true&$filter=receivedDateTime ge {today}"
        inbox_response = anvil.http.request(inbox_url, method="GET", headers=headers, json=True)
        inbox_count = inbox_response.get_bytes().get("@odata.count", 0)

        # Get sent message count for today
        sent_url = f"{MICROSOFT_GRAPH_API_BASE_URL}/users/{user_id}/mailFolders/SentItems/messages?$count=true&$filter=sentDateTime ge {today}"
        sent_response = anvil.http.request(sent_url, method="GET", headers=headers, json=True)
        sent_count = sent_response.get_bytes().get("@odata.count", 0)

        return {"user": email, "inbox_count": inbox_count, "sent_count": sent_count}

    except anvil.http.HttpError as e:
        print(f"HTTPError fetching email stats for {email}: {e.status_code} {e.content}")
        return {"user": email, "inbox_count": 0, "sent_count": 0}
    except Exception as e:
        print(f"Error fetching email stats for {email}: {e}")
        return {"user": email, "inbox_count": 0, "sent_count": 0}
