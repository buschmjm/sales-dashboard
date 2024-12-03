import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import http.client


# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
@anvil.server.callable
conn = http.client.HTTPSConnection("api.goto.com")

conn.request("GET", "/call-reports/v1/reports/user-activity?organizationId=0127d974-f9f3-0704-2dee-000100422009")

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))