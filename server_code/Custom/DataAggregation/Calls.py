# Reports Server-Side Code
import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

@anvil.server.callable
def get_call_data(queryStart, queryEnd):
    queryData = app_tables.call_statistics.search(
        reportDate=q.between(queryStart, queryEnd, min_inclusive=True, max_inclusive=True)
    )

    # Ensure queryData is iterable and not empty
    if not queryData:
        return {"columns": [], "values": []}

    # Extract column names properly
    first_row = queryData[0]
    print(f"First row: {first_row}")

    # Use first_row to extract column names
    if first_row:
        column_names = list(first_row.keys())  # Properly extract column names from the Row object
    else:
        column_names = []

    print(f"Column names: {column_names}")

    # Validate column names are strings
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

    print(f"User values: {user_values}")

    return {"columns": column_names, "values": user_values}
