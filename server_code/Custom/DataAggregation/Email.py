import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.http
import pytz
from datetime import datetime
from ..APICalls.Outlook import get_access_token, fetch_user_stats

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
    today = datetime.now(cst_tz).strftime('%Y-%m-%dT00:00:00Z')

    for user in app_users:
        email = user["email"]
        if not email:
            continue

        # Fetch stats using the API module
        user_stats = fetch_user_stats(email, headers, today)
        results.append(user_stats)

    return results
