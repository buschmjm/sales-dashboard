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
        # Convert dates to strings in the same format as stored in the database
        start_str = datetime.combine(start_date, time.min).strftime("%m/%d/%Y %H:%M:%S")
        end_str = datetime.combine(end_date, time.max).strftime("%m/%d/%Y %H:%M:%S")
        
        # Get all rows within date range using string comparison with between
        rows = app_tables.b2b.search(
            tables.order_by("sales_rep"),  # Changed from Sales_Rep to sales_rep
            timestamp=q.between(start_str, end_str)
        )
        
        # Count occurrences per sales rep
        metric_counts = {}
        sales_reps = set()
        
        for row in rows:
            sales_rep = row['sales_rep']  # Changed from Sales_Rep to sales_rep
            sales_reps.add(sales_rep)
            
            # Convert metric name to match database columns
            db_metric = metric.lower().replace(' ', '_')  # Convert 'Business Cards' to 'business_cards'
            if row[db_metric]:  # If the selected metric is True for this row
                metric_counts[sales_rep] = metric_counts.get(sales_rep, 0) + 1
        
        results = {
            "users": sorted(list(sales_reps)) or ["No Data"],
            "metrics": metric_counts
        }
        
        return results
        
    except Exception as e:
        print(f"Error in get_b2b_stats: {e}")
        return None
