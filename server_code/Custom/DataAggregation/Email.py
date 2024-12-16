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
def update_outlook_statistics_db(results):
    """Update the database with email statistics"""
    try:
        if not results:
            return False
            
        today = datetime.now().date()
        
        for result in results:
            # Get existing record for today
            existing = app_tables.outlook_statistics.search(
                userId=result['user'],
                reportDate=today
            )
            
            stats = {
                'userId': result['user'],
                'userName': result['user'].split('@')[0],  # Simple username from email
                'reportDate': today,
                'inbound': result.get('inbox_count', 0),
                'outbound': result.get('sent_count', 0),
                'total': result.get('inbox_count', 0) + result.get('sent_count', 0)
            }
            
            # Update or create record
            if existing:
                for row in existing:
                    row.update(**stats)
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
        rows = app_tables.outlook_statistics.search(
            tables.order_by("userId"),
            reportDate=q.between(start_date, end_date)
        )
        
        users = set()
        metrics = {'total': {}, 'inbound': {}, 'outbound': {}}
        
        for row in rows:
            user = row['userId']
            users.add(user)
            
            metrics['inbound'][user] = metrics['inbound'].get(user, 0) + row['inbound']
            metrics['outbound'][user] = metrics['outbound'].get(user, 0) + row['outbound']
            metrics['total'][user] = metrics['total'].get(user, 0) + row['total']
        
        return {
            "users": sorted(list(users)) or ["No Data"],
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error in get_email_stats: {e}")
        return {"users": ["No Data"], "metrics": {'total': {}, 'inbound': {}, 'outbound': {}}}
