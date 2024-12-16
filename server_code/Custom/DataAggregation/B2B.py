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
        # Convert dates to datetime objects
        start_datetime = datetime.combine(start_date, time.min)  # Start of day
        end_datetime = datetime.combine(end_date, time.max)    # End of day
        
        # Get all rows within date range
        rows = app_tables.b2b.search(
            tables.order_by("Sales_Rep"),
            Timestamp=q.between(start_datetime, end_datetime)
        )
        
        # Count occurrences per sales rep
        metric_counts = {}
        sales_reps = set()
        
        for row in rows:
            sales_rep = row['Sales_Rep']
            sales_reps.add(sales_rep)
            
            if row[metric]:  # If the selected metric is True for this row
                metric_counts[sales_rep] = metric_counts.get(sales_rep, 0) + 1
        
        results = {
            "users": sorted(list(sales_reps)) or ["No Data"],
            "metrics": metric_counts
        }
        
        return results
        
    except Exception as e:
        print(f"Error in get_b2b_stats: {e}")
        return None
