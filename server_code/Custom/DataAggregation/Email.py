import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import pytz

@anvil.server.callable
def update_outlook_statistics_db(stats_data):
    """Update or create outlook statistics records for users."""
    # Get current date in CST timezone
    cst_tz = pytz.timezone("America/Chicago")
    today = datetime.now(cst_tz).date()
    
    for stat in stats_data:
        # Get user details
        user = app_tables.users.get(email=stat["user"])
        if not user:
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

@anvil.server.callable
def get_email_stats(start_date, end_date):
    """Fetch and aggregate email statistics for the specified date range."""
    try:
        # Debug input parameters
        print(f"Fetching email stats for date range: {start_date} to {end_date}")
        
        # Query the database for email statistics
        results = app_tables.outlook_statistics.search(
            tables.order_by('reportDate', ascending=True),
            reportDate=q.between(start_date, end_date)
        )
        
        # Convert results to list to check if empty
        results_list = [dict(r) for r in results]
        print(f"Found {len(results_list)} records")
        
        if not results_list:
            print("No email statistics found for the specified date range")
            # Return dummy data for testing (remove in production)
            return {
                'users': ['No Data'],
                'metrics': {
                    'total': [0],
                    'inbound': [0],
                    'outbound': [0]
                }
            }
        
        # Aggregate data by user
        user_totals = {}
        for row in results_list:
            user_name = row['userName']
            if user_name not in user_totals:
                user_totals[user_name] = {
                    'total': 0,
                    'inbound': 0,
                    'outbound': 0
                }
            
            # Sum up the values for each metric
            user_totals[user_name]['total'] += row['total']
            user_totals[user_name]['inbound'] += row['inbound']
            user_totals[user_name]['outbound'] += row['outbound']
        
        response = {
            'users': list(user_totals.keys()),
            'metrics': {
                'total': [user_totals[user]['total'] for user in user_totals],
                'inbound': [user_totals[user]['inbound'] for user in user_totals],
                'outbound': [user_totals[user]['outbound'] for user in user_totals]
            }
        }
        
        print(f"Returning aggregated stats for {len(response['users'])} users")
        return response
        
    except Exception as e:
        print(f"Error in get_email_stats: {str(e)}")
        raise
