import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import requests

def get_b2b_stats_for_today():
    """Get B2B statistics from Google Sheet for today"""
    try:
        today = datetime.now().date()
        api_key = anvil.secrets.get_secret("b2b_sheets_secret")
        url = "https://script.google.com/macros/s/AKfycbzrm6ttNyYRxfibYUHYExxlWruT33m1gXdDRZFo4hLFap0zkmhutKKkHdpQNW27GdS4Yw/exec"
        
        response = requests.get(
            url,
            params={"key": api_key},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"API request failed: {response.status_code}")
            return {'business_cards': 0, 'flyers': 0, 'b2b_emails': 0}
            
        sheet_data = response.json()
        today_str = today.strftime("%Y-%m-%d")
        
        # Initialize counters
        totals = {'business_cards': 0, 'flyers': 0, 'b2b_emails': 0}
        count = 0
        
        for row in sheet_data:
            try:
                timestamp_str = row.get('Timestamp', '').strip()
                if not timestamp_str:
                    continue
                    
                try:
                    timestamp = datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                        
                if timestamp.date() == today:
                    promo_material = row.get('Promotional Material the customer would like?', '').lower()
                    if 'business card' in promo_material:
                        totals['business_cards'] += 1
                    if 'flyer' in promo_material:
                        totals['flyers'] += 1
                    if 'email' in promo_material:
                        totals['b2b_emails'] += 1
                    count += 1
                    
            except Exception as row_error:
                print(f"Error processing B2B row: {str(row_error)}")
                continue
                
        # Calculate averages
        if count > 0:
            return {k: v/count for k, v in totals.items()}
        return totals
        
    except Exception as e:
        print(f"Error getting B2B stats: {e}")
        return {'business_cards': 0, 'flyers': 0, 'b2b_emails': 0}

def get_b2b_stats_for_user(user_email):
    """Get B2B statistics from Google Sheet for a specific user"""
    try:
        today = datetime.now().date()
        api_key = anvil.secrets.get_secret("b2b_sheets_secret")
        url = "https://script.google.com/macros/s/AKfycbzrm6ttNyYRxfibYUHYExxlWruT33m1gXdDRZFo4hLFap0zkmhutKKkHdpQNW27GdS4Yw/exec"
        
        response = requests.get(
            url,
            params={"key": api_key},
            timeout=30
        )
        
        if response.status_code != 200:
            return {'business_cards': 0, 'flyers': 0, 'b2b_emails': 0}
            
        sheet_data = response.json()
        
        # Initialize counters
        totals = {'business_cards': 0, 'flyers': 0, 'b2b_emails': 0}
        
        for row in sheet_data:
            try:
                if row.get('Sales Rep', '').strip().lower() != user_email.lower():
                    continue
                    
                timestamp_str = row.get('Timestamp', '').strip()
                if not timestamp_str:
                    continue
                    
                try:
                    timestamp = datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                        
                if timestamp.date() == today:
                    promo_material = row.get('Promotional Material the customer would like?', '').lower()
                    if 'business card' in promo_material:
                        totals['business_cards'] += 1
                    if 'flyer' in promo_material:
                        totals['flyers'] += 1
                    if 'email' in promo_material:
                        totals['b2b_emails'] += 1
                    
            except Exception as row_error:
                print(f"Error processing B2B row: {str(row_error)}")
                continue
                
        return totals
        
    except Exception as e:
        print(f"Error getting user B2B stats: {e}")
        return {'business_cards': 0, 'flyers': 0, 'b2b_emails': 0}

@anvil.server.callable
def calculate_average_rep_stats():
    """Calculate and store average rep statistics for the current date"""
    try:
        today = datetime.now().date()
        print(f"\n=== Calculating Average Rep Stats for {today} ===")
        
        # Get all records for today
        call_stats = app_tables.call_statistics.search(reportDate=today)
        email_stats = app_tables.outlook_statistics.search(reportDate=today)
        
        print("\n--- Call Statistics Input Data ---")
        call_data = []
        for row in call_stats:
            call_data.append({
                'user': row['userId'],
                'time': row['totalDuration'],
                'volume': row['volume']
            })
            print(f"User: {row['userId']}")
            print(f"  - Call Time: {row['totalDuration']} minutes")
            print(f"  - Call Volume: {row['volume']} calls")
            
        print("\n--- Email Statistics Input Data ---")
        email_data = []
        for row in email_stats:
            email_data.append({
                'user': row['userId'],
                'sent': row['outbound'],
                'received': row['inbound']
            })
            print(f"User: {row['userId']}")
            print(f"  - Emails Sent: {row['outbound']}")
            print(f"  - Emails Received: {row['inbound']}")
            
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
        if call_data:
            stats['calls_time'] = sum(d['time'] for d in call_data) / len(call_data)
            stats['call_volume'] = sum(d['volume'] for d in call_data) / len(call_data)
            print(f"\nCall Averages (from {len(call_data)} users):")
            print(f"  - Average Call Time: {stats['calls_time']:.2f} minutes")
            print(f"  - Average Call Volume: {stats['call_volume']:.2f} calls")
        
        # Calculate email averages
        if email_data:
            stats['emails_sent'] = sum(d['sent'] for d in email_data) / len(email_data)
            stats['emails_received'] = sum(d['received'] for d in email_data) / len(email_data)
            print(f"\nEmail Averages (from {len(email_data)} users):")
            print(f"  - Average Emails Sent: {stats['emails_sent']:.2f}")
            print(f"  - Average Emails Received: {stats['emails_received']:.2f}")
            
        # Get B2B averages from Google Sheet
        print("\n--- Fetching B2B Statistics ---")
        b2b_stats = get_b2b_stats_for_today()
        print("B2B Averages:")
        print(f"  - Average Business Cards: {b2b_stats['business_cards']:.2f}")
        print(f"  - Average Flyers: {b2b_stats['flyers']:.2f}")
        print(f"  - Average B2B Emails: {b2b_stats['b2b_emails']:.2f}")
        stats.update(b2b_stats)
            
        # Update or create average_rep record
        existing = app_tables.average_rep.get(date=today)
        if existing:
            existing.update(**stats)
            print("\nUpdated existing average_rep record")
        else:
            app_tables.average_rep.add_row(**stats)
            print("\nCreated new average_rep record")
            
        print("\n=== Final Average Statistics ===")
        for key, value in stats.items():
            if key != 'date':
                print(f"{key}: {value:.2f}")
                
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
        
        # First attempt to get average rep data
        avg_rep = app_tables.average_rep.get(date=today)
        
        # If no data exists, calculate it first
        if not avg_rep:
            print("No average rep data found for today, calculating...")
            success = calculate_average_rep_stats()
            if success:
                avg_rep = app_tables.average_rep.get(date=today)
                if not avg_rep:
                    raise ValueError("Failed to create average rep data")
            else:
                raise ValueError("Failed to calculate average rep stats")
        
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
            
        # Get B2B data from Google Sheets
        b2b_stats = get_b2b_stats_for_user(user_email)
        user_data.update(b2b_stats)
        
        # Convert avg_rep data to dictionary for consistent access
        avg_data = {
            'calls_time': avg_rep['calls_time'],
            'call_volume': avg_rep['call_volume'],
            'emails_sent': avg_rep['emails_sent'],
            'emails_received': avg_rep['emails_received'],
            'business_cards': avg_rep['business_cards'],
            'flyers': avg_rep['flyers'],
            'b2b_emails': avg_rep['b2b_emails']
        }
            
        return {
            'user': user_data,
            'average': avg_data
        }
        
    except Exception as e:
        print(f"Error getting comparison data: {e}")
        return None

@anvil.server.callable
def recalculate_todays_averages():
    """Force recalculation of today's averages, called by refresh button"""
    try:
        today = datetime.now().date()
        print(f"\n=== Force Recalculating Average Rep Stats for {today} ===")
        
        # Delete existing record for today if it exists
        existing = app_tables.average_rep.get(date=today)
        if existing:
            print("Removing existing average rep record for today")
            existing.delete()
            
        # Recalculate averages
        result = calculate_average_rep_stats()
        print(f"Force recalculation completed: {result}")
        return result
        
    except Exception as e:
        print(f"Error in force recalculation: {e}")
        return False
