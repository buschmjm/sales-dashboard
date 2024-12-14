import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta
import pytz

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
    """Fetch and aggregate email statistics for the specified date range."""
    try:
        # Convert date parameters efficiently
        if isinstance(start_date, (datetime, str)):
            start_date = start_date.date() if isinstance(start_date, datetime) else datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, (datetime, str)):
            end_date = end_date.date() if isinstance(end_date, datetime) else datetime.strptime(end_date, '%Y-%m-%d').date()
            
        # Single query with optimized filtering
        results = app_tables.outlook_statistics.search(
            tables.order_by('reportDate'),
            reportDate=q.all_of(
                q.greater_than_or_equal_to(start_date),
                q.less_than(end_date + timedelta(days=1))
            )
        )
        
        # Process results efficiently
        if not list(results):
            return {'users': ['No Data'], 'metrics': {'total': [0], 'inbound': [0], 'outbound': [0]}}
        
        # Single-pass aggregation
        user_totals = {}
        for row in results:
            user_name = row['userName']
            if user_name not in user_totals:
                user_totals[user_name] = {'total': 0, 'inbound': 0, 'outbound': 0}
            
            totals = user_totals[user_name]
            totals['total'] += row['total']
            totals['inbound'] += row['inbound']
            totals['outbound'] += row['outbound']
        
        # Prepare response in single pass
        users = list(user_totals.keys())
        return {
            'users': users,
            'metrics': {
                metric: [user_totals[user][metric] for user in users]
                for metric in ['total', 'inbound', 'outbound']
            }
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {'users': ['No Data'], 'metrics': {'total': [0], 'inbound': [0], 'outbound': [0]}}
