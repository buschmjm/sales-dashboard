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
        print("Starting update_outlook_statistics_db")  # Debug log
        if not results:
            print("No results to update")
            return False
            
        print(f"Processing {len(results)} email records")  # Debug log
        today = datetime.now().date()
        updated = 0
        
        for result in results:
            try:
                if not result or 'user' not in result:
                    print(f"Skipping invalid result: {result}")
                    continue
                
                # Getting existing record with correct column names
                existing = app_tables.outlook_statistics.get(
                    userId=result['user'],
                    reportDate=today
                )
                
                # Prepare stats with correct column names
                stats = {
                    'userId': result['user'],
                    'userName': result['user'].split('@')[0],
                    'reportDate': today,
                    'inbound': int(result.get('inbox_count', 0)),
                    'outbound': int(result.get('sent_count', 0)),
                    'total': int(result.get('inbox_count', 0)) + int(result.get('sent_count', 0))
                }
                
                print(f"Processing stats for {stats['userId']}")
                
                if existing:
                    print(f"Updating existing record")
                    existing.update(**stats)
                else:
                    print(f"Creating new record")
                    app_tables.outlook_statistics.add_row(**stats)
                    
                updated += 1
                
            except Exception as e:
                print(f"Error processing individual result: {e}")
                continue
                
        print(f"Successfully updated {updated} records")
        return updated > 0
        
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
