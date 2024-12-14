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
        # Add one day to end_date to include the end date in results
        end_date = end_date + timedelta(days=1)
        print(f"Adjusted date range: {start_date} to {end_date}")
        
        # Query the database for email statistics with explicit date comparison
        results = app_tables.outlook_statistics.search(
            tables.order_by('reportDate', ascending=True),
            reportDate=q.greater_than_or_equal_to(start_date),
            reportDate=q.less_than(end_date)
        )
        
        # Convert results to list and debug
        results_list = [dict(r) for r in results]
        print(f"Found {len(results_list)} records")
        if results_list:
            print("Date range of results:", min(r['reportDate'] for r in results_list),
                  "to", max(r['reportDate'] for r in results_list))
        
        if not results_list:
            print("No email statistics found for the specified date range")
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
