import anvil.server
from anvil.tables import app_tables

@anvil.server.callable
def get_call_data():
  queryData = app_tables.call_statistics