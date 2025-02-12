import anvil.secrets
import anvil.server
import requests
import json
import base64
from anvil.tables import app_tables
from datetime import datetime, timedelta

# ===============================================
# Configuration
# ===============================================
def get_credentials():
    """Get GoTo credentials from database"""
    try:
        creds = app_tables.tokens.search()
        for row in creds:
            return {
                'client_id': row.get('Client ID', ''),
                'client_secret': row.get('Secret', ''),
                'access_token': row.get('access_token', ''),
                'personal_key': row.get('Personal Access Key', '')
            }
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

# Remove hardcoded credentials
CLIENT_ID = None
CLIENT_SECRET = None
ACCESS_TOKEN = None
REFRESH_TOKEN = None

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
    try:
        tokens = app_tables.tokens.search()
        token_row = None
        for t in tokens:
            token_row = t
            break
        if token_row:
            ACCESS_TOKEN = token_row['access_token']
            REFRESH_TOKEN = token_row['refresh_token']
    except Exception as e:
        print(f"Error loading tokens: {e}")

def save_tokens(access_token, refresh_token):
    """Save ACCESS_TOKEN and REFRESH_TOKEN to the tokens table, replacing any existing rows."""
    try:
        for row in app_tables.tokens.search():
            row.delete()
        app_tables.tokens.add_row(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        print(f"Error saving tokens: {e}")

# ===============================================
# Utility Functions
# ===============================================
def encode_client_credentials(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

# Load any previously saved tokens
load_tokens()

@anvil.server.callable
def verify_existing_credentials():
    """Verify and set up existing credentials from the tokens table"""
    try:
        # Get all rows from tokens table
        token_rows = list(app_tables.tokens.search())
        print(f"Found {len(token_rows)} rows in tokens table")
        
        if not token_rows:
            print("No credentials found in tokens table")
            return False
            
        # Get the first row since we expect only one
        creds = token_rows[0]
        print("Found existing credentials row")
        
        # Print available columns (for debugging)
        print(f"Available columns: {[col['name'] for col in app_tables.tokens.list_columns()]}")
        
        # Try to get the Personal Access Key
        if 'Personal Access Key' in creds:
            access_key = creds['Personal Access Key']
            print(f"Found Personal Access Key: {access_key[:10]}...")
            
            # Store it as our access token
            global ACCESS_TOKEN
            ACCESS_TOKEN = access_key
            
            # Test the access token
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Accept": "application/json"
            }
            
            # Make a test API call
            now = datetime.utcnow()
            test_url = f"{CALL_REPORTS_URL}?startTime={now.isoformat()}Z&endTime={now.isoformat()}Z"
            
            print("\nTesting existing credentials...")
            response = requests.get(test_url, headers=headers)
            
            print(f"Test API response status: {response.status_code}")
            
            if response.status_code in (200, 404):
                print("Credentials verified successfully!")
                return True
            else:
                print(f"API test failed: {response.text}")
                return False
                
        else:
            print("No Personal Access Key found in credentials")
            return False
            
    except Exception as e:
        print(f"Error verifying credentials: {str(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        return False

@anvil.server.callable
def get_api_keys():
    """Server function to get API keys from the database"""
    try:
        api_keys = app_tables.api_keys.search()
        result = None
        for row in api_keys:
            result = {
                'client_id': row['Client ID'],
                'client_secret': row['Secret'],
                'personal_key': row['Personal Access Key']
            }
            break  # Just get the first row
        return result
    except Exception as e:
        print(f"Error getting API keys: {str(e)}")
        return None

def get_and_verify_credentials():
    """Get credentials from all possible sources and verify them"""
    try:
        print("\nAttempting to gather credentials from all sources...")
        credentials = None
        
        # 1. Try tokens table first (local access)
        try:
            token_rows = list(app_tables.tokens.search())
            if token_rows:
                row = token_rows[0]
                credentials = {
                    'client_id': row.get('Client ID', ''),
                    'client_secret': row.get('Secret', ''),
                    'personal_key': row.get('Personal Access Key', '')
                }
                print("Found credentials in tokens table")
        except Exception as e:
            print(f"Error checking tokens table: {str(e)}")
        
        # 2. Try API Keys table through server function
        if not credentials:
            try:
                api_creds = get_api_keys()  # Direct call since we're already server-side
                if api_creds:
                    credentials = api_creds
                    print("Found credentials in API Keys table")
            except Exception as e:
                print(f"Error getting API keys: {str(e)}")
        
        # 3. Try Anvil secrets
        secret_cred = anvil.secrets.get_secret('client_secret')
        if secret_cred and credentials:
            print("Found client_secret in Anvil secrets")
            credentials['client_secret'] = secret_cred
        
        # Verify and use the credentials
        if credentials and credentials.get('personal_key'):
            print(f"Found complete credentials with Personal Access Key")
            if verify_credentials(credentials):
                return True
            
        print("No valid credentials found or verification failed")
        return False
        
    except Exception as e:
        print(f"Error in get_and_verify_credentials: {str(e)}")
        return False

def verify_credentials(creds):
    """Verify if the given credentials work"""
    try:
        if not creds.get('personal_key'):
            print("No Personal Access Key available")
            return False
            
        # Clean and validate the personal access key
        personal_key = creds['personal_key'].strip()
        if not personal_key:
            print("Personal Access Key is empty after cleaning")
            return False
            
        print(f"\nCredential Verification Details:")
        print(f"Key Length: {len(personal_key)}")
        
        # GoTo API expects OAuth tokens in JWT format
        # If the key doesn't look like a JWT, try to format it properly
        if '_' in personal_key and not personal_key.count('.') == 2:
            # Format appears to be in the old style with underscore
            # Convert to proper Bearer token format if needed
            parts = personal_key.split('_')
            if len(parts) == 2:
                personal_key = parts[1]  # Use the second part after underscore
                print("Reformatted key from underscore format")
                
        print(f"Final Key Format: {personal_key[:10]}...")
        
        headers = {
            "Authorization": f"Bearer {personal_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Use current time window for test
        now = datetime.utcnow()
        start_time = (now - timedelta(minutes=5)).isoformat() + 'Z'
        end_time = now.isoformat() + 'Z'
        
        test_url = f"{CALL_REPORTS_URL}?startTime={start_time}&endTime={end_time}"
        
        print("\nMaking API Test Call:")
        print(f"URL: {test_url}")
        print(f"Authorization: Bearer {personal_key[:10]}...")
        
        response = requests.get(test_url, headers=headers)
        
        print(f"\nAPI Response:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in (200, 404):
            print("\nCredentials verified successfully!")
            
            # Set global access token
            global ACCESS_TOKEN
            ACCESS_TOKEN = personal_key
            
            try:
                # Update tokens table with verified credentials
                for row in app_tables.tokens.search():
                    row.delete()
                
                app_tables.tokens.add_row(
                    **{
                        'Client ID': creds.get('client_id', ''),
                        'Secret': creds.get('client_secret', ''),
                        'Personal Access Key': personal_key,
                        'access_token': personal_key,
                        'last_verified': datetime.utcnow()
                    }
                )
            except Exception as e:
                print(f"Warning: Could not update tokens table: {e}")
            
            return True
            
        elif response.status_code == 401:
            print("\nAuthentication failed (401):")
            print("1. Your Personal Access Key may be expired")
            print("2. Generate a new key in GoTo Admin Portal")
            print("3. Ensure the key has 'call-reports:read' permission")
            print(f"Error details: {response.text}")
        else:
            print(f"\nUnexpected response: {response.status_code}")
            print(f"Error details: {response.text}")
            
        return False
        
    except Exception as e:
        print(f"\nError in verify_credentials: {str(e)}")
        return False

@anvil.server.callable
def test_goto_connection():
    """Test GoTo API connection and return detailed diagnostics"""
    try:
        creds = get_credentials()
        if not creds:
            return {"success": False, "error": "No credentials found"}
            
        if not creds.get('personal_key'):
            return {"success": False, "error": "No Personal Access Key found"}
            
        headers = {
            "Authorization": f"Bearer {creds['personal_key']}",
            "Accept": "application/json"
        }
        
        now = datetime.utcnow()
        five_mins_ago = now - timedelta(minutes=5)
        test_url = f"{CALL_REPORTS_URL}?startTime={five_mins_ago.isoformat()}Z&endTime={now.isoformat()}Z"
        
        response = requests.get(test_url, headers=headers)
        
        return {
            "success": response.status_code in (200, 404),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.text[:500],  # First 500 chars
            "url": test_url,
            "key_preview": f"{creds['personal_key'][:5]}...{creds['personal_key'][-5:]}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def initialize_auth():
    """Initialize authorization using all possible credential sources"""
    if get_and_verify_credentials():
        return True
        
    print("Failed to initialize using any credential source")
    return False

# Remove or comment out unused OAuth-related functions
# def refresh_access_token():
# def handle_oauth_callback():

# ===============================================
# Update Data Table with API Data
# ===============================================
def update_call_statistics(data):
    today_date = datetime.utcnow().date()

    for item in data.get("items", []):
        user_id = item["userId"]
        user_name = item["userName"]
        data_values = item["dataValues"]

        # Check if a record exists for this user ID and today's date
        existing_row = app_tables.call_statistics.get(
            userId=user_id, reportDate=today_date
        )

        if existing_row:
            # Update the existing record
            existing_row.update(
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
            )
        else:
            # Add a new record
            app_tables.call_statistics.add_row(
                userId=user_id,
                userName=user_name,
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
                reportDate=today_date,
            )

# ===============================================
# Fetch Call Reports (Manual Trigger)
# ===============================================
@anvil.server.callable
def fetch_call_reports():
    global ACCESS_TOKEN
    
    if not ACCESS_TOKEN:
        if not initialize_auth():
            raise Exception("Failed to initialize authorization. Please check your credentials.")
    
    # Calculate startTime as the start of today and endTime as the current time in UTC
    now = datetime.utcnow()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = start_of_today.isoformat() + "Z"
    end_time = now.isoformat() + "Z"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    url = f"{CALL_REPORTS_URL}?startTime={start_time}&endTime={end_time}"

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        print("Access token expired. Attempting to refresh...")
        refresh_access_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        update_call_statistics(data)
        return {"message": "Data refreshed successfully."}
    elif response.status_code == 404:
        return {"message": "No data found for the specified time frame."}
    else:
        raise Exception(f"Failed to fetch call data: {response.status_code} - {response.text}")

@anvil.server.callable
def initialize_goto_credentials(client_id, client_secret, personal_access_key):
    """Initialize GoTo credentials in the tokens table"""
    try:
        # Clean up the personal access key
        personal_access_key = personal_access_key.strip()
        if '_' in personal_access_key:
            parts = personal_access_key.split('_')
            if len(parts) == 2:
                personal_access_key = parts[1]
        
        # Create credentials dictionary
        creds = {
            'client_id': client_id.strip(),
            'client_secret': client_secret.strip(),
            'personal_key': personal_access_key
        }
        
        # Verify the credentials
        if verify_credentials(creds):
            print("Successfully initialized GoTo credentials")
            return True
            
        print("Credentials verification failed")
        return False
        
    except Exception as e:
        print(f"Error initializing credentials: {e}")
        return False

@anvil.server.callable
def debug_tokens_table():
    """Debug function to check tokens table structure and content"""
    try:
        # Get table columns
        columns = [col['name'] for col in app_tables.tokens.list_columns()]
        print(f"Available columns in tokens table: {columns}")
        
        # Get existing rows
        rows = list(app_tables.tokens.search())
        print(f"Number of rows in tokens table: {len(rows)}")
        
        # Show row content if any exists
        for row in rows:
            print("\nRow data:")
            for col in columns:
                # Mask sensitive data
                value = row.get(col, 'Not set')
                if col in ['Secret', 'Personal Access Key', 'access_token']:
                    if value:
                        value = f"{value[:5]}...{value[-5:]}"
                print(f"{col}: {value}")
                
        return True
        
    except Exception as e:
        print(f"Error debugging tokens table: {str(e)}")
        return False

@anvil.server.callable
def add_token_row():
    """Add a single row to tokens table with proper column names"""
    try:
        # Clear existing rows
        for row in app_tables.tokens.search():
            row.delete()
            
        # Add new row with empty values to see structure
        app_tables.tokens.add_row(
            **{
                'Client ID': '',
                'Secret': '',
                'Personal Access Key': '',
                'access_token': '',
                'refresh_token': None
            }
        )
        return True
    except Exception as e:
        print(f"Error adding token row: {str(e)}")
        return False

@anvil.server.callable
def debug_goto_auth():
    """Debug function to check GoTo authentication setup"""
    try:
        print("\nDebug GoTo Auth:")
        print("1. Checking tokens table...")
        
        token_rows = list(app_tables.tokens.search())
        print(f"Found {len(token_rows)} rows in tokens table")
        
        if token_rows:
            row = token_rows[0]
            columns = [col['name'] for col in app_tables.tokens.list_columns()]
            print(f"\nAvailable columns: {columns}")
            
            for col in columns:
                value = row.get(col, 'Not set')
                if col in ['Secret', 'Personal Access Key', 'access_token']:
                    if value:
                        value = f"{value[:5]}...{value[-5:]}"
                print(f"{col}: {value}")
                
        print("\n2. Checking API Keys table...")
        api_keys = get_api_keys()
        if api_keys:
            print("Found API keys")
            for key, value in api_keys.items():
                masked_value = f"{value[:5]}...{value[-5:]}" if value else 'Not set'
                print(f"{key}: {masked_value}")
                
        print("\n3. Testing API Connection...")
        test_result = test_goto_connection()
        print(f"Test result: {json.dumps(test_result, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"Error in debug_goto_auth: {str(e)}")
        return False

