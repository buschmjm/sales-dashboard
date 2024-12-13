import anvil.files
from anvil.files import data_files
import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

@anvil.server.callable
def get_call_data(queryStart, queryEnd):
    """Fetch call data for a specific date range."""
    # Fetch query data based on provided date range
    queryData = list(app_tables.call_statistics.search(
        reportDate=q.between(queryStart, queryEnd, min_inclusive=True, max_inclusive=True)
    ))

    # Return empty result if no data is found
    if not queryData:
        return {"columns": [], "values": []}

    # Fetch column metadata from the data table schema
    column_metadata = app_tables.call_statistics.list_columns()  # Get full metadata of columns
    column_names = [col['name'] for col in column_metadata]  # Extract column names

    # Validate column names as strings
    if not all(isinstance(col, str) for col in column_names):
        raise ValueError("Column names must be strings.")

    # Extract user values
    try:
        user_values = [
            [row[col] for col in column_names] for row in queryData
        ]
    except KeyError as e:
        raise ValueError(f"Error accessing column data: {e}")
    except Exception as e:
        raise ValueError(f"Error processing row data: {e}")

    # Print count of user value sets instead of full details
    print(f"Number of user value sets: {len(user_values)}")

    return {"columns": column_names, "values": user_values}
