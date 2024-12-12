import anvil.server
from datetime import date
from anvil.tables import app_tables

@anvil.server.callable
def get_call_data(queryStart, queryEnd):
    queryData = app_tables.call_statistics.search(
        reportDate=q.between(queryStart, queryEnd, min_inclusive=True, max_inclusive=True)
    )
    if not queryData:
        raise ValueError("No data found for the specified date range.")
    return queryData
