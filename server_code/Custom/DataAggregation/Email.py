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
    if not stats_data:
        print("No stats data provided to update")
        return

    # Get current date in CST timezone
    cst_tz = pytz.timezone("America/Chicago")
    today = datetime.now(cst_tz).date()
    
    print(f"Updating statistics for date: {today}")
    updated_count = 0
    created_count = 0

    for stat in stats_data:
        try:
            # Get user details
            user = app_tables.users.get(email=stat["user"])
            if not user:
                print(f"No user found for email: {stat['user']}")
                continue
                
            # Calculate total emails
            total_emails = stat["inbox_count"] + stat["sent_count"]
            
            # Look for existing record for this user and date
            existing_record = app_tables.outlook_statistics.get(
                userId=stat["user"],
                reportDate=today
            )
            
            if existing_record:
                # Update existing record
                existing_record.update(
                    inbound=stat["inbox_count"],
                    outbound=stat["sent_count"],
                    total=total_emails
                )
                updated_count += 1
            else:
                # Create new record
                app_tables.outlook_statistics.add_row(
                    userId=stat["user"],
                    userName=user["name"],
                    inbound=stat["inbox_count"],
                    outbound=stat["sent_count"],
                    total=total_emails,
                    reportDate=today
                )
                created_count += 1

        except Exception as e:
            print(f"Error updating stats for user {stat.get('user')}: {e}")

    print(f"Statistics update complete. Updated: {updated_count}, Created: {created_count}")

@anvil.server.callable
def get_email_stats(start_date, end_date):
    """Fetch and aggregate email statistics with caching."""
    try:
        cache_key = f"{start_date}_{end_date}"
        current_time = datetime.now().timestamp()
        
        # Check cache first
        if cache_key in _stats_cache:
            cached_data, timestamp = _stats_cache[cache_key]
            if current_time - timestamp < CACHE_DURATION:
                return cached_data

        # Optimize query by adding indexes and using single query
        results = app_tables.outlook_statistics.search(
            tables.order_by('reportDate', ascending=True),
            reportDate=q.all_of(
                q.greater_than_or_equal_to(start_date),
                q.less_than_or_equal_to(end_date)
            )
        )

        # Process results in batches
        user_totals = {}
        for row in results:
            user_name = row['userName']
            if user_name not in user_totals:
                user_totals[user_name] = {'total': 0, 'inbound': 0, 'outbound': 0}
            
            totals = user_totals[user_name]
            totals['total'] += row['total']
            totals['inbound'] += row['inbound']
            totals['outbound'] += row['outbound']

        # Prepare response efficiently
        if not user_totals:
            response = {'users': ['No Data'], 'metrics': {'total': [0], 'inbound': [0], 'outbound': [0]}}
        else:
            users = list(user_totals.keys())
            response = {
                'users': users,
                'metrics': {
                    metric: [user_totals[user][metric] for user in users]
                    for metric in ['total', 'inbound', 'outbound']
                }
            }

        # Cache the results
        _stats_cache[cache_key] = (response, current_time)
        return response

    except Exception as e:
        print(f"Error in get_email_stats: {e}")
        return {'users': ['No Data'], 'metrics': {'total': [0], 'inbound': [0], 'outbound': [0]}}
