import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Import the main functions from their respective modules
from .APICalls.GoTo import fetch_call_reports
from .APICalls.Outlook import fetch_user_email_stats

@anvil.server.background_task
def fetch_call_reports_scheduled():
    fetch_call_reports()

@anvil.server.background_task
def fetch_user_email_stats_scheduled():
    fetch_user_email_stats()
