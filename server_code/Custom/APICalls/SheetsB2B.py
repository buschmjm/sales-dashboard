import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests

def fetch_google_sheet_data(sales_rep=None, complete=None):
    # Get the secret key from Anvil's Secrets Service
    api_key = anvil.secrets.get_secret("5Up3rS3cr3t_K3y!2024#@Xz")
    
    # API URL
    url = "https://script.google.com/macros/s/AKfycbzrm6ttNyYRxfibYUHYExxlWruT33m1gXdDRZFo4hLFap0zkmhutKKkHdpQNW27GdS4Yw/exec"
    
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
