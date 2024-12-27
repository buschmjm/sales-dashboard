# Reports Client-Side Code
from ._anvil_designer import EmailReportsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, date
from .. import theme_service


class EmailReports(EmailReportsTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Set table role and styling
        if hasattr(self, 'repeating_panel_1'):
            self.repeating_panel_1.role = 'table'
            self.repeating_panel_1.tag.style = """
                width: 100%;
                margin-top: 16px;
            """
        
        # Set default date range for emails
        self.email_end_date.date = date.today()
        self.email_start_date.date = date.today() - timedelta(days=7)

        # Set up email metrics dropdown with consistent naming
        self.metric_display_names = {
            'total': 'Total Emails',
            'inbound': 'Emails Received',
            'outbound': 'Emails Sent'
        }
        
        self.email_metric_selector.items = [
            (name, key) for key, name in self.metric_display_names.items()
        ]
        self.email_metric_selector.selected_value = 'total'

        # Bind events
        self.email_metric_selector.set_event_handler('change', self.email_metric_changed)
        self.email_start_date.set_event_handler('change', self.email_date_change)
        self.email_end_date.set_event_handler('change', self.email_date_change)

        self.refresh_email_data()

    def email_metric_changed(self, **event_args):
        """Handle metric selector change"""
        self.refresh_email_data()  # Refresh data when metric changes

    def email_date_change(self, **event_args):
        """Handle email statistics date picker changes"""
        self.refresh_email_data()

    def refresh_email_data(self):
        """Fetch and display email data based on current date range."""
        try:
            start_date = self.email_start_date.date
            end_date = self.email_end_date.date

            # Get statistics without forcing refresh every time
            data = anvil.server.call("get_email_stats", start_date, end_date)
            self._update_email_plot(data)

        except Exception as e:
            alert("Failed to refresh email data")
            print(f"Error: {e}")

    def _get_display_name(self, email):
        """Get user's display name from users table, fallback to email if not found"""
        try:
            user = app_tables.users.get(email=email)
            if user is None:
                return email
            # Access the name directly from the row object
            return user['name'] if user['name'] else email
        except Exception as e:
            print(f"Error getting display name for {email}: {e}")
            return email

    def _update_email_plot(self, data):
        """Update the email statistics plot with a vertical bar chart."""
        try:
            if not data or "users" not in data or "metrics" not in data:
                self._show_empty_plot()
                return

            users = data["users"]
            if users == ["No Data"]:
                self._show_empty_plot()
                return

            metric = self.email_metric_selector.selected_value or 'total'
            metric_display_name = self.metric_display_names[metric]

            # Create a trace for each user with proper display name
            traces = []
            for email in users:
                display_name = self._get_display_name(email)
                value = data["metrics"][metric].get(email, 0)  # Get value before modifying email
                traces.append({
                    "type": "bar",
                    "name": display_name,
                    "x": [display_name],
                    "y": [value],
                    "showlegend": True
                })

            self.email_numbers_plot.data = traces
            self.email_numbers_plot.layout = {
                "title": f"Email Statistics ({self.email_start_date.date} - {self.email_end_date.date})",
                "xaxis": {
                    "title": None,
                    "tickangle": -45,
                    "showticklabels": True,
                    "type": "category"  # Ensures proper category spacing
                },
                "yaxis": {"title": "Number of Emails"},
                "showlegend": True,
                "barmode": 'group',  # Changed from 'stack' to 'group' to match phone
                "margin": {
                    "l": 50,
                    "r": 150,  # Increased right margin for legend
                    "b": 100,
                    "t": 50,
                    "pad": 4
                },
                "legend": {
                    "yanchor": "top",
                    "y": 1,
                    "xanchor": "left",
                    "x": 1.02,
                    "bgcolor": "transparent",  # Removed background color
                    "bordercolor": "transparent",  # Removed border
                    "borderwidth": 0,
                    "font": {"size": 10},
                    "clickmode": "toggleitem"  # Changed to match phone report behavior
                },
                "dragmode": False,  # Disable zooming/panning
                "hovermode": "closest",
                'paper_bgcolor': theme_service.theme.get_color('Background'),
                'plot_bgcolor': theme_service.theme.get_color('Background'),
                'font': {'color': theme_service.theme.get_color('Text')},
            }

        except Exception as e:
            self._show_empty_plot(str(e))

    def _show_empty_plot(self, error=None):
        """Helper method to show empty plot state."""
        message = "No Email Statistics Available" if not error else f"Error: {error}"
        self.email_numbers_plot.data = []  # Clear existing traces
        self.email_numbers_plot.layout.update({
            "title": message,
            "xaxis": {"title": None},
            "yaxis": {"title": "Number of Emails"},
            "showlegend": False,
            "margin": {
                "l": 50,
                "r": 150,
                "b": 100,
                "t": 50,
                "pad": 4
            },
            "legend": {
                "bgcolor": "transparent",
                "bordercolor": "transparent",
                "borderwidth": 0
            }
        })
