import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, time

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

@anvil.server.callable
def get_b2b_stats(start_date, end_date, metric):
    """Get B2B statistics for the given date range and metric"""
    try:
        print(f"Querying B2B stats for {metric} from {start_date} to {end_date}")  # Debug log
        
        # Convert dates to strings in the same format as stored in the database
        start_str = datetime.combine(start_date, time.min).strftime("%m/%d/%Y %H:%M:%S")
        end_str = datetime.combine(end_date, time.max).strftime("%m/%d/%Y %H:%M:%S")
        
        # Debug log the query parameters
        print(f"Searching with timestamp between {start_str} and {end_str}")
        
        # Get all rows within date range
        all_rows = list(app_tables.b2b.search())  # First get all rows to verify data exists
        print(f"Total rows in b2b table: {len(all_rows)}")  # Debug log
        
        # Now do the actual filtered search
        rows = app_tables.b2b.search(
            tables.order_by("sales_rep"),
            timestamp=q.between(start_str, end_str)
        )
        
        # Convert rows to list to get length
        rows_list = list(rows)
        print(f"Filtered rows: {len(rows_list)}")  # Debug log
        
        # Rest of the processing
        metric_counts = {}
        sales_reps = set()
        
        metric_map = {
            'Email': 'email',
            'Flyers': 'flyers',
            'Business Cards': 'business_cards'
        }
        
        db_metric = metric_map.get(metric)
        print(f"Looking for metric: {db_metric}")  # Debug log
        
        if not db_metric:
            raise ValueError(f"Invalid metric: {metric}")
            
        for row in rows_list:
            sales_rep = row['sales_rep']
            sales_reps.add(sales_rep)
            
            if row[db_metric]:  # If the metric is True for this row
                metric_counts[sales_rep] = metric_counts.get(sales_rep, 0) + 1
        
        results = {
            "users": sorted(list(sales_reps)) or ["No Data"],
            "metrics": metric_counts
        }
        
        print(f"Found {len(sales_reps)} sales reps with data")
        print(f"Metric counts: {metric_counts}")  # Debug log
        return results
        
    except Exception as e:
        print(f"Error in get_b2b_stats: {e}")
        print(f"Full error details: {str(e)}")  # More detailed error logging
        return None
