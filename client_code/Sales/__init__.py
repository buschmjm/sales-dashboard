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
        self.init_components(**properties)
        # Set default date range to last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        self.end_date_selector.date = end_date
        self.start_date_selector.date = start_date
        self.refresh_data()
        
    def refresh_data(self):
        """Refresh all plots with current user data"""
        try:
            current_user = anvil.users.get_user()
            if not current_user:
                raise ValueError("No user logged in")
            
            start_date = self.start_date_selector.date
            end_date = self.end_date_selector.date
            
            data = anvil.server.call('get_comparison_data', 
                                   current_user['email'],
                                   start_date,
                                   end_date)
            if not data:
                raise ValueError("No data available")
                
            self._update_plots(data)
            
        except Exception as e:
            alert("Failed to load sales data")
            print(f"Error refreshing data: {e}")

    def update_button_click(self, **event_args):
        """Update button click handler"""
        self.refresh_data()
            
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
            
            # Create comparison bar chart
            plot.data = [
                {
                    "type": "bar",
                    "name": "You",
                    "x": ["Current"],
                    "y": [data['user'][metric]],
                    "marker": {"color": "#1f77b4"}
                },
                {
                    "type": "bar",

                    "name": "Average Rep",
                    "x": ["Current"],
                    "y": [data['average'][metric]],
                    "marker": {"color": "#ff7f0e"}
                }
            ]
            
            plot.layout = {
                "title": title,
                "showlegend": True,
                "xaxis": {"showticklabels": False},
                "yaxis": {"title": y_label},
                "barmode": "group",
                "margin": {"l": 50, "r": 50, "t": 50, "b": 30}
            }
    def drop_down_1_change(self, **event_args):
      """This method is called when an item is selected"""
      pass