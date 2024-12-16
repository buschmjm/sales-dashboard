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
            print("No results to update")
            return False
            
        today = datetime.now().date()
        updated = 0
        
        for result in results:
            user_id = result['user']
            if not user_id:
                continue
                
            # First try to find existing record
            existing = app_tables.outlook_statistics.get(
                userId=user_id,
                reportDate=today
            )
            
            stats = {
                'userId': user_id,
                'userName': result['user'].split('@')[0],
                'reportDate': today,
                'inbound': int(result.get('inbox_count', 0)),
                'outbound': int(result.get('sent_count', 0)),
                'total': int(result.get('inbox_count', 0)) + int(result.get('sent_count', 0))
            }
            
            if existing:
                existing.update(**stats)
            else:
                app_tables.outlook_statistics.add_row(**stats)
            updated += 1
                
        print(f"Successfully updated {updated} records")
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
