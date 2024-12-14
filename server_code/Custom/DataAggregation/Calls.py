import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q
from datetime import datetime

# Add cache for call data
_call_data_cache = {}
CACHE_DURATION = 300  # 5 minutes in seconds

@anvil.server.callable
def get_call_data(queryStart, queryEnd):
    """Get call data with caching and optimized querying."""
    try:
        cache_key = f"{queryStart}_{queryEnd}"
        current_time = datetime.now().timestamp()
        
        # Check cache first
        if cache_key in _call_data_cache:
            cached_data, timestamp = _call_data_cache[cache_key]
            if current_time - timestamp < CACHE_DURATION:
                return cached_data

        # Optimize query with specific column selection and indexing
        queryData = app_tables.call_statistics.search(
            tables.order_by('reportDate', ascending=True),
            reportDate=q.between(queryStart, queryEnd)
        )

        # Early return for empty data
        if not queryData:
            return {"columns": [], "values": []}

        # Get column names once
        column_metadata = app_tables.call_statistics.list_columns()
        column_names = [col['name'] for col in column_metadata]

        # Batch process rows efficiently
        user_values = []
        batch_size = 100
        current_batch = []

        for row in queryData:
            current_batch.append([row[col] for col in column_names])
            
            if len(current_batch) >= batch_size:
                user_values.extend(current_batch)
                current_batch = []
        
        if current_batch:
            user_values.extend(current_batch)

        result = {"columns": column_names, "values": user_values}
        
        # Cache the results
        _call_data_cache[cache_key] = (result, current_time)
        return result

    except Exception as e:
        print(f"Error in get_call_data: {e}")
        return {"columns": [], "values": []}
