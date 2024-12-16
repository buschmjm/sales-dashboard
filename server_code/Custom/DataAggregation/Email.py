import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta
import pytz

# Add cache dictionary
_stats_cache = {}
CACHE_DURATION = 300  # 5 minutes in seconds

@anvil.server.callable
def update_outlook_statistics_db(stats_data):
    """Update or create outlook statistics records for users."""
    try:
        today = datetime.now().date()
        
        for user_data in stats_data:
            # Get existing record for today
            existing = app_tables.outlook_statistics.get(
                user=user_data['user'],
                date=today
            )
            
            stats = {
                'user': user_data['user'],
                'date': today,
                'inbox_count': user_data.get('inbox_count', 0),
                'sent_count': user_data.get('sent_count', 0)
            }
            
            if existing:
                existing.update(**stats)
            else:
                app_tables.outlook_statistics.add_row(**stats)
                
        return True
        
    except Exception as e:
        print(f"Error updating outlook statistics: {e}")
        return False

@anvil.server.callable
def get_email_stats(start_date, end_date):
    """Get email statistics for the given date range"""
    try:
        # Get all rows within date range
        rows = app_tables.outlook_statistics.search(
            tables.order_by("user"),
            date=q.between(start_date, end_date)
        )
        
        # Process statistics
        users = set()
        metrics = {'total': {}, 'inbound': {}, 'outbound': {}}
        
        for row in rows:
            user = row['user']
            users.add(user)
            
            # Aggregate metrics
            inbound = row.get('inbox_count', 0)
            outbound = row.get('sent_count', 0)
            
            metrics['inbound'][user] = metrics['inbound'].get(user, 0) + inbound
            metrics['outbound'][user] = metrics['outbound'].get(user, 0) + outbound
            metrics['total'][user] = metrics['inbound'][user] + metrics['outbound'][user]
        
        return {
            "users": sorted(list(users)) or ["No Data"],
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error in get_email_stats: {e}")
        return {"users": ["No Data"], "metrics": {'total': {}, 'inbound': {}, 'outbound': {}}}
