import anvil.server
from datetime import datetime, timedelta
from anvil.tables import app_tables

@anvil.server.callable
def get_call_data(queryStart, queryEnd):
  queryData = app_tables.call_statistics.search(reportDate = q.between(queryStart, queryEnd, min_inclusive=True, max_inclusive = True)))
  return queryData