import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta
import statistics

@anvil.server.callable
def calculate_average_rep_stats():
    """Calculate and store average rep statistics for the current date"""
    try:
        today = datetime.now().date()
        print(f"Calculating average rep stats for {today}")
        
        # Initialize stats dictionary
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
        
        # Get call statistics
        call_rows = app_tables.call_statistics.search(reportDate=today)
        call_times = []
        call_volumes = []
        
        for row in call_rows:
            call_times.append(row['totalDuration'])
            call_volumes.append(row['volume'])
            
        if call_times:
            stats['calls_time'] = statistics.mean(call_times)
        if call_volumes:
            stats['call_volume'] = statistics.mean(call_volumes)
            
        # Get email statistics
        email_rows = app_tables.outlook_statistics.search(reportDate=today)
        sent_counts = []
        received_counts = []
        
        for row in email_rows:
            sent_counts.append(row['outbound'])
            received_counts.append(row['inbound'])
            
        if sent_counts:
            stats['emails_sent'] = statistics.mean(sent_counts)
        if received_counts:
            stats['emails_received'] = statistics.mean(received_counts)
            
        # Get B2B statistics
        b2b_rows = app_tables.b2b_statistics.search(reportDate=today)
        cards = []
        flyers = []
        emails = []
        
        for row in b2b_rows:
            cards.append(row['business_cards'])
            flyers.append(row['flyers'])
            emails.append(row['emails'])
            
        if cards:
            stats['business_cards'] = statistics.mean(cards)
        if flyers:
            stats['flyers'] = statistics.mean(flyers)
        if emails:
            stats['b2b_emails'] = statistics.mean(emails)
            
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
