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
        today = datetime.now().date()
        
        for user_data in results:
            # Get existing record for today
            existing = app_tables.outlook_statistics.get(
                userId=user_data['user'],  # Changed from 'user' to 'userId'
                reportDate=today
            )
            
            stats = {
                'userId': user_data['user'],  # Changed from 'user' to 'userId'
                'userName': user_data.get('user_name', user_data['user']),  # Added userName
                'reportDate': today,
                'inbound': user_data.get('inbox_count', 0),  # Changed to match column name
                'outbound': user_data.get('sent_count', 0),  # Changed to match column name
                'total': user_data.get('inbox_count', 0) + user_data.get('sent_count', 0)  # Calculate total
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
            tables.order_by("userId"),
            reportDate=q.between(start_date, end_date)
        )
        
        # Process statistics
        users = set()
        metrics = {'total': {}, 'inbound': {}, 'outbound': {}}
        
        for row in rows:
            user_id = row['userId']  # Changed from 'user' to 'userId'
            users.add(user_id)
            
            # Use correct column names
            metrics['inbound'][user_id] = metrics['inbound'].get(user_id, 0) + row['inbound']
            metrics['outbound'][user_id] = metrics['outbound'].get(user_id, 0) + row['outbound']
            metrics['total'][user_id] = metrics['total'].get(user_id, 0) + row['total']
        
        return {
            "users": sorted(list(users)) or ["No Data"],
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error in get_email_stats: {e}")
        return {"users": ["No Data"], "metrics": {'total': {}, 'inbound': {}, 'outbound': {}}}
