from ._anvil_designer import SalesTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta

class Sales(SalesTemplate):
    def __init__(self, **properties):
        # Initialize components first
        self.init_components(**properties)
        
        # Set default date range
        self.end_date_picker.date = datetime.now().date()
        self.start_date_picker.date = self.end_date_picker.date - timedelta(days=7)
        
        # Setup user selector for admins
        self.setup_user_selector()
        
        # Initial data load (today only)
        self.refresh_data()
        
    def setup_user_selector(self):
        """Configure user selector dropdown for admins"""
        try:
            current_user = anvil.users.get_user()
            user_row = app_tables.users.get(email=current_user['email'])
            
            # Default to invisible
            self.user_select.visible = False
            
            if user_row and user_row['Admin']:
                # Get all sales users, sorted alphabetically
                sales_users = app_tables.users.search(
                    Sales=True,
                    tables.order_by('name')
                )
                
                # Format items for dropdown
                self.user_select.items = [(u['name'], u['email']) for u in sales_users]
                
                # Make visible and select first user
                self.user_select.visible = True
                if self.user_select.items:
                    self.user_select.selected_value = self.user_select.items[0][1]
                    
        except Exception as e:
            print(f"Error setting up user selector: {e}")
            
    def get_target_user_email(self):
        """Get the email of the user whose data should be displayed"""
        current_user = anvil.users.get_user()
        if self.user_select.visible:
            return self.user_select.selected_value
        return current_user['email']
        
    def search_button_click(self, **event_args):
        """Handle search button click"""
        try:
            # Show loading indicator
            notification = Notification("Loading data...", timeout=None)
            notification.show()
            
            start_date = self.start_date_picker.date
            end_date = self.end_date_picker.date
            user_email = self.get_target_user_email()
            
            # Get data for date range
            data = anvil.server.call(
                'get_date_range_comparison',
                user_email,
                start_date,
                end_date
            )
            
            if data:
                self._update_plots(data)
            else:
                raise ValueError("No data available")
                
            notification.hide()
            
        except Exception as e:
            alert("Failed to load comparison data")
            print(f"Error loading comparison data: {e}")
            
    def refresh_data(self):
        """Refresh all plots with current user data"""
        try:
            current_user = anvil.users.get_user()
            if not current_user:
                raise ValueError("No user logged in")
                
            data = anvil.server.call('get_comparison_data', current_user['email'])
            if not data:
                raise ValueError("No data available")
                
            self._update_plots(data)
            
        except Exception as e:
            alert("Failed to load sales data")
            print(f"Error refreshing data: {e}")
            
    def _update_plots(self, data):
        """Update all plots with comparison data"""
        plots_config = {
            'calls_time_plot': ('Calls Time', 'Minutes'),
            'call_volume_plot': ('Call Volume', 'Calls'),
            'emails_sent_plot': ('Emails Sent', 'Count'),
            'emails_received_plot': ('Emails Received', 'Count'),
            'business_cards_plot': ('Business Cards', 'Count'),
            'flyers_plot': ('Flyers', 'Count'),
            'b2b_emails_plot': ('B2B Emails', 'Count')
        }
        
        for plot_name, (title, y_label) in plots_config.items():
            metric = plot_name.replace('_plot', '')
            plot = getattr(self, plot_name)
            
            # Create comparison bar chart with dates
            plot.data = [
                {
                    "type": "bar",
                    "name": "You",
                    "x": data['dates'],
                    "y": [d[metric] for d in data['user']],
                    "marker": {"color": "#1f77b4"}
                },
                {
                    "type": "bar",
                    "name": "Average Rep",
                    "x": data['dates'],
                    "y": [d[metric] for d in data['average']],
                    "marker": {"color": "#ff7f0e"}
                }
            ]
            
            plot.layout = {
                "title": title,
                "showlegend": True,
                "xaxis": {
                    "title": "Date",
                    "tickangle": -45,
                    "type": "category"
                },
                "yaxis": {"title": y_label},
                "barmode": "group",
                "margin": {"l": 50, "r": 50, "t": 50, "b": 100}
            }