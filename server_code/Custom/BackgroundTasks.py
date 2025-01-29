import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Import the main functions from their respective modules
from .APICalls.GoTo import fetch_call_reports, initialize_auth
from .APICalls.Outlook import fetch_user_email_stats

@anvil.server.background_task
def fetch_call_reports_scheduled():
    try:
        fetch_call_reports()
    except Exception as e:
        print(f"Error in scheduled call reports: {str(e)}")
        # Try to reinitialize auth and fetch again
        if "Access token not available" in str(e):
            if initialize_auth():
                fetch_call_reports()
            else:
                print("Failed to reinitialize authorization")

@anvil.server.background_task
def fetch_user_email_stats_scheduled():
    fetch_user_email_stats()
