import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests

def fetch_google_sheet_data(sales_rep=None, complete=None):
    # Get the secret key from Anvil's Secrets Service
    api_key = anvil.secrets.get_secret("GOOGLE_SHEETS_API_KEY")
    
    # API URL
    url = "https://script.google.com/macros/s/<YOUR_DEPLOYMENT_ID>/exec"
    
    # Query parameters
    params = {
        "key": api_key
    }
    
    # Add filters if provided
    if sales_rep:
        params["Sales Rep"] = sales_rep
    if complete:
        params["Complete"] = complete
    
    # Make the GET request
    response = requests.get(url, params=params)
    
    # Check for errors
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")
    
    # Return the parsed JSON response
    return response.json()
