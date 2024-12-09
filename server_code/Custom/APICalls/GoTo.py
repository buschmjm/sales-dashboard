import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import http.client
import requests
import json

# Configuration
ACCESS_TOKEN = "eyJraWQiOiI2MjAiLCJhbGciOiJSUzUxMiJ9.eyJzYyI6ImNhbGwtY29udHJvbC52MS5jYWxscy5jb250cm9sIGNhbGxzLnYyLmluaXRpYXRlIG1lc3NhZ2luZy52MS53cml0ZSBpZGVudGl0eTpzY2ltLm1lIGNhbGwtZXZlbnRzLnYxLmV2ZW50cy5yZWFkIG1lc3NhZ2luZy52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB2b2ljZW1haWwudjEubm90aWZpY2F0aW9ucy5tYW5hZ2UgcmVjb3JkaW5nLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIHN1cHBvcnQ6IHZvaWNlbWFpbC52MS52b2ljZW1haWxzLndyaXRlIGZheC52MS53cml0ZSB2b2ljZS1hZG1pbi52MS53cml0ZSBpZGVudGl0eTogd2VicnRjLnYxLnJlYWQgd2VicnRjLnYxLndyaXRlIGNvbGxhYjogdm9pY2UtYWRtaW4udjEucmVhZCBwcmVzZW5jZS52MS5yZWFkIHJlY29yZGluZy52MS5yZWFkIGNhbGwtZXZlbnRzLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIGlkZW50aXR5OnNjaW0ub3JnIHByZXNlbmNlLnYxLndyaXRlIGZheC52MS5yZWFkIGNhbGwtaGlzdG9yeS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBwcmVzZW5jZS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBtZXNzYWdpbmcudjEuc2VuZCBtZXNzYWdpbmcudjEucmVhZCBjci52MS5yZWFkIGZheC52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB1c2Vycy52MS5saW5lcy5yZWFkIHZvaWNlbWFpbC52MS52b2ljZW1haWxzLnJlYWQiLCJzdWIiOiIxOTIxNzAxNTU0NjE0MDIxMzk4IiwiYXVkIjoiMjA5M2ZjYjMtZGQzNS00MzIwLWI1YmYtMWU5MmU3ZWYwMDMyIiwib2duIjoicHdkIiwibHMiOiJhMjI0NzlmOC00MTRiLTRkYzYtOWIwNC1kNDhiY2MwNzlmN2QiLCJ0eXAiOiJhIiwiZXhwIjoxNzMzNzc5NDY2LCJpYXQiOjE3MzM3NzU4NjYsImp0aSI6ImNhZGNmODlkLTgwNjItNDAwYi1iNzViLTBjMWE4YWRjN2Q4OCIsImxvYSI6M30.P-bZsArlW6QWey1okPCzgjLZYBQM3ghzNMfGxMSFxEQv8tnq5gqOrn1DLZt5Pi-v46uqo9S-ax8mbAznM7Q3vM_DveU1JvuAIT34BYA9tsqrg7Jc-FrHyj6AE8XRnvJXKKHO45A5BG3EILakmeqcQUrMmpfhd-OYHjIPAmspW5LwKMwdV0lH98zlUmnEsENFlWh7WI8-JXYOpUav-e-F4ozd9zgzIr6MXPHgsliUpKKoeZ9SbaBunj4SU0sOYf47-vhv4fFdRnwRBbu1b8zl08EMtK_xGbdNBLmVCqp4OorBpGx7qswNRc1e22mK4tfsaZnGok1Pij4fFW62Fw1aEA"
REFRESH_TOKEN = "eyJraWQiOiI2MjAiLCJhbGciOiJSUzUxMiJ9.eyJzYyI6ImNhbGwtY29udHJvbC52MS5jYWxscy5jb250cm9sIGNhbGxzLnYyLmluaXRpYXRlIG1lc3NhZ2luZy52MS53cml0ZSBpZGVudGl0eTpzY2ltLm1lIGNhbGwtZXZlbnRzLnYxLmV2ZW50cy5yZWFkIG1lc3NhZ2luZy52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB2b2ljZW1haWwudjEubm90aWZpY2F0aW9ucy5tYW5hZ2UgcmVjb3JkaW5nLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIHN1cHBvcnQ6IHZvaWNlbWFpbC52MS52b2ljZW1haWxzLndyaXRlIGZheC52MS53cml0ZSB2b2ljZS1hZG1pbi52MS53cml0ZSBpZGVudGl0eTogd2VicnRjLnYxLnJlYWQgd2VicnRjLnYxLndyaXRlIGNvbGxhYjogdm9pY2UtYWRtaW4udjEucmVhZCBwcmVzZW5jZS52MS5yZWFkIHJlY29yZGluZy52MS5yZWFkIGNhbGwtZXZlbnRzLnYxLm5vdGlmaWNhdGlvbnMubWFuYWdlIGlkZW50aXR5OnNjaW0ub3JnIHByZXNlbmNlLnYxLndyaXRlIGZheC52MS5yZWFkIGNhbGwtaGlzdG9yeS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBwcmVzZW5jZS52MS5ub3RpZmljYXRpb25zLm1hbmFnZSBtZXNzYWdpbmcudjEuc2VuZCBtZXNzYWdpbmcudjEucmVhZCBjci52MS5yZWFkIGZheC52MS5ub3RpZmljYXRpb25zLm1hbmFnZSB1c2Vycy52MS5saW5lcy5yZWFkIHZvaWNlbWFpbC52MS52b2ljZW1haWxzLnJlYWQiLCJzdWIiOiIxOTIxNzAxNTU0NjE0MDIxMzk4IiwiYXVkIjoiMjA5M2ZjYjMtZGQzNS00MzIwLWI1YmYtMWU5MmU3ZWYwMDMyIiwib2duIjoicHdkIiwidHlwIjoiciIsImV4cCI6MTczNjM2Nzg2NiwiaWF0IjoxNzMzNzc1ODY2LCJqdGkiOiI1MDBhYWMwYy0zY2FkLTQ5NWYtYTJmMS0zZWFhNWFhZWFmYjAiLCJsb2EiOjN9.1F04PPQEGDQG9ufoaFRknXxyI_29-5__WXG-lENrY03HwqlS7Nj_9zgLdQF4RhuMr4nUn7pvkKM0rDOp_hlcYpCbclT0FfJZMPakWF5VdRWtHg2zjw5u2fLQu2QzL8p4P3Fz89UeuEeXSAC5TbIugaKkZR8-K_SgsquMX6wWwaWutPE-u6Q_Y_0g5FYlcoz9erQuAWCbq-51zWWLqijrtCT2pPXO1ilskq8wg9lgacohL9T5I5AV0NXGvma0uSSrsM8wAZg2xK-WyPhf89vRqaPaVRGdVfVDOV2xkldzeJPvQEKbQ6u6u25--6G2mrAV7HaiZTV-gIbovozZctMGNw"
CLIENT_ID = "2093fcb3-dd35-4320-b5bf-1e92e7ef0032"
CLIENT_SECRET = "tEJzrrwv8SMVNBEH6OCTSZWg"
TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
CALL_REPORTS_URL = "https://api.goto.com/call-reports/v1/reports/user-activity"

# Fetch call data using http.client
@anvil.server.callable
def fetch_call_reports_http():
    conn = http.client.HTTPSConnection("api.goto.com")
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    conn.request("GET", "/call-reports/v1/reports/user-activity?organizationId=0127d974-f9f3-0704-2dee-000100422009", headers=headers)
    res = conn.getresponse()

    if res.status == 401:
        # Token expired, refresh it
        refresh_access_token()
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        conn.request("GET", "/call-reports/v1/reports/user-activity?organizationId=0127d974-f9f3-0704-2dee-000100422009", headers=headers)
        res = conn.getresponse()

    data = res.read()
    return json.loads(data.decode("utf-8"))

# Fetch call data using requests
@anvil.server.callable
def fetch_call_reports_requests():
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{CALL_REPORTS_URL}?organizationId=0127d974-f9f3-0704-2dee-000100422009", 
        headers=headers
    )

    if response.status_code == 401:
        # Token expired, refresh it
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

# Refresh the access token
def refresh_access_token():
    global ACCESS_TOKEN
    global REFRESH_TOKEN

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=payload)

    if response.status_code == 200:
        tokens = response.json()
        ACCESS_TOKEN = tokens["access_token"]
        REFRESH_TOKEN = tokens.get("refresh_token", REFRESH_TOKEN)
    else:
        raise Exception(f"Failed to refresh access token: {response.status_code} - {response.text}")

# Example callable function
@anvil.server.callable
def say_hello(name):
    print(f"Hello, {name}!")
    return 42
