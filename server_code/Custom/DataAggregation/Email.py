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
    """Fetch email statistics for the specified date range and return in client-friendly format."""
    # Query the database for email statistics
    results = app_tables.outlook_statistics.search(
        tables.order_by('reportDate', ascending=True),
        reportDate=q.between(start_date, end_date)
    )
    
    # Format the data similar to call statistics
    columns = ['userId', 'userName', 'reportDate', 'total', 'inbound', 'outbound']
    values = []
    
    for row in results:
        values.append([
            row['userId'],
            row['userName'],
            row['reportDate'],
            row['total'],
            row['inbound'],
            row['outbound']
        ])
    
    return {
        "columns": columns,
        "values": values
    }
