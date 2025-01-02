import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime

@anvil.server.callable
def calculate_average_rep_stats():
    """Calculate and store average rep statistics for the current date"""
    try:
        today = datetime.now().date()
        print(f"Calculating average rep stats for {today}")
        
        # Get all records for today
        call_stats = app_tables.call_statistics.search(reportDate=today)
        email_stats = app_tables.outlook_statistics.search(reportDate=today)
        b2b_stats = app_tables.b2b_statistics.search(reportDate=today)
        
        # Calculate averages
        stats = {
            'date': today,
            'calls_time': 0,
            'call_volume': 0,
            'emails_sent': 0,
            'emails_received': 0,
            'business_cards': 0,
            'flyers': 0,
            'b2b_emails': 0
        }
        
        # Calculate call averages
        call_count = 0
        for row in call_stats:
            stats['calls_time'] += row['totalDuration']
            stats['call_volume'] += row['volume']
            call_count += 1
            
        if call_count > 0:
            stats['calls_time'] /= call_count
            stats['call_volume'] /= call_count
            
        # Calculate email averages
        email_count = 0
        for row in email_stats:
            stats['emails_sent'] += row['outbound']
            stats['emails_received'] += row['inbound']
            email_count += 1
            
        if email_count > 0:
            stats['emails_sent'] /= email_count
            stats['emails_received'] /= email_count
            
        # Calculate B2B averages
        b2b_count = 0
        for row in b2b_stats:
            stats['business_cards'] += row['business_cards']
            stats['flyers'] += row['flyers']
            stats['b2b_emails'] += row['emails']
            b2b_count += 1
            
        if b2b_count > 0:
            stats['business_cards'] /= b2b_count
            stats['flyers'] /= b2b_count
            stats['b2b_emails'] /= b2b_count
            
        # Update or create average_rep record
        existing = app_tables.average_rep.get(date=today)
        if existing:
            existing.update(**stats)
        else:
            app_tables.average_rep.add_row(**stats)
            
        print(f"Successfully updated average rep stats for {today}")
        return True
        
    except Exception as e:
        print(f"Error calculating average rep stats: {e}")
        return False

@anvil.server.background_task
def calculate_average_rep_stats_scheduled():
    """Scheduled task to calculate average rep statistics"""
    print("Starting scheduled average rep calculation")
    result = calculate_average_rep_stats()
    print(f"Scheduled average rep calculation completed: {result}")
    return result

@anvil.server.callable
def get_comparison_data(user_email):
    """Get comparison data between a specific user and average rep"""
    try:
        today = datetime.now().date()
        
        # Get average rep data
        avg_rep = app_tables.average_rep.get(date=today)
        if not avg_rep:
            calculate_average_rep_stats()
            avg_rep = app_tables.average_rep.get(date=today)
            
        if not avg_rep:
            raise ValueError("No average rep data available")
            
        # Get user's data
        user_data = {
            'calls_time': 0,
            'call_volume': 0,
            'emails_sent': 0,
            'emails_received': 0,
            'business_cards': 0,
            'flyers': 0,
            'b2b_emails': 0
        }
        
        # Get call data
        call_row = app_tables.call_statistics.get(
            reportDate=today,
            userId=user_email
        )
        if call_row:
            user_data['calls_time'] = call_row['totalDuration']
            user_data['call_volume'] = call_row['volume']
            
        # Get email data
        email_row = app_tables.outlook_statistics.get(
            reportDate=today,
            userId=user_email
        )
        if email_row:
            user_data['emails_sent'] = email_row['outbound']
            user_data['emails_received'] = email_row['inbound']
            
        # Get B2B data
        b2b_row = app_tables.b2b_statistics.get(
            reportDate=today,
            userId=user_email
        )
        if b2b_row:
            user_data['business_cards'] = b2b_row['business_cards']
            user_data['flyers'] = b2b_row['flyers']
            user_data['b2b_emails'] = b2b_row['emails']
            
        return {
            'user': user_data,
            'average': {k: getattr(avg_rep, k) for k in user_data.keys()}
        }
        
    except Exception as e:
        print(f"Error getting comparison data: {e}")
        return None
