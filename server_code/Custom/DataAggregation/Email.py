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
            
        print(f"Starting database update with {len(results)} records")
        today = datetime.now().date()
        updated_count = 0
        
        for user_stats in results:
            try:
                user_id = user_stats['user']
                print(f"Processing stats for {user_id}")
                
                # Get existing record with proper error handling
                try:
                    existing = app_tables.outlook_statistics.get(
                        userId=user_id,
                        reportDate=today
                    )
                except Exception as db_error:
                    print(f"Database lookup error: {db_error}")
                    continue
                
                stats = {
                    'userId': user_id,
                    'userName': user_id.split('@')[0],
                    'reportDate': today,
                    'inbound': int(user_stats.get('inbox_count', 0)),
                    'outbound': int(user_stats.get('sent_count', 0)),
                    'total': int(user_stats.get('inbox_count', 0)) + int(user_stats.get('sent_count', 0))
                }
                
                if existing:
                    existing.update(**stats)
                    print(f"Updated existing record for {user_id}")
                else:
                    app_tables.outlook_statistics.add_row(**stats)
                    print(f"Created new record for {user_id}")
                    
                updated_count += 1
                    
            except Exception as e:
                print(f"Error updating stats for {user_id}: {e}")
                continue
                
        print(f"Successfully updated {updated_count} records")
        return updated_count > 0
        
    except Exception as e:
        print(f"Error in update_outlook_statistics_db: {e}")
        return False

@anvil.server.callable
def get_email_stats(start_date, end_date):
    """Get email statistics for the given date range"""
    try:
        print(f"Fetching email stats from {start_date} to {end_date}")  # Debug log
        
        # Get data using correct column names
        rows = app_tables.outlook_statistics.search(
            tables.order_by("userId"),
            reportDate=q.between(start_date, end_date)
        )
        rows_list = list(rows)  # Convert to list for length check
        print(f"Found {len(rows_list)} records")  # Debug log
        
        users = set()
        metrics = {'total': {}, 'inbound': {}, 'outbound': {}}
        
        for row in rows_list:
            user = row['userId']  # Using correct column name
            users.add(user)
            
            # Use the correct column names
            metrics['inbound'][user] = metrics['inbound'].get(user, 0) + row['inbound']
            metrics['outbound'][user] = metrics['outbound'].get(user, 0) + row['outbound']
            metrics['total'][user] = metrics['total'].get(user, 0) + row['total']
            
        print(f"Processed data for {len(users)} users")  # Debug log
        
        return {
            "users": sorted(list(users)) or ["No Data"],
            "metrics": metrics
        }
        
    except Exception as e:
        print(f"Error in get_email_stats: {str(e)}")
        print(f"Full error details: {repr(e)}")
        return {"users": ["No Data"], "metrics": {'total': {}, 'inbound': {}, 'outbound': {}}}
