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
        print(f"Querying B2B stats for {metric} from {start_date} to {end_date}")
        
        # Convert dates to datetime objects for comparison
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        
        # Map metric names to database columns
        metric_map = {
            'Email': 'email',
            'Flyers': 'flyers',
            'Business Cards': 'business_cards'
        }
        
        db_metric = metric_map.get(metric)
        if not db_metric:
            raise ValueError(f"Invalid metric: {metric}")
            
        # Get rows where the metric is True and timestamp is in range
        rows = app_tables.b2b.search(
            tables.order_by("sales_rep"),
            q.all_of(
                timestamp=q.between(start_dt, end_dt),
                **{db_metric: True}
            )
        )
        
        # Count metrics per sales rep
        metric_counts = {}
        sales_reps = set()
        
        for row in rows:
            sales_rep = row['sales_rep']
            sales_reps.add(sales_rep)
            metric_counts[sales_rep] = metric_counts.get(sales_rep, 0) + 1
        
        print(f"Found {len(sales_reps)} sales reps with {metric} data")
        print(f"Counts: {metric_counts}")
        
        return {
            "users": sorted(list(sales_reps)) or ["No Data"],
            "metrics": metric_counts
        }
        
    except Exception as e:
        print(f"Error in get_b2b_stats: {e}")
        return {"users": ["No Data"], "metrics": {}}
