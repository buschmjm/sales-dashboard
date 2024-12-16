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

            # Single trace with all users
            plot_data = {
                "type": "bar",
                "x": users,
                "y": [data["metrics"][metric].get(user, 0) for user in users],
                "name": metric_display_name,
                "showlegend": True
            }

            self.email_numbers_plot.data = [plot_data]
            self.email_numbers_plot.layout = {
                "title": f"Email Statistics ({self.email_start_date.date} - {self.email_end_date.date})",
                "xaxis": {
                    "title": None,
                    "tickangle": -45,
                    "showticklabels": True
                },
                "yaxis": {"title": "Number of Emails"},
                "showlegend": True,
                "barmode": 'stack',
                "margin": {"b": 100, "t": 30, "r": 100},  # Added right margin for legend
                "legend": {
                    "yanchor": "top",
                    "y": 1,
                    "xanchor": "left",
                    "x": 1.02,  # Position legend to the right of the plot
                    "bgcolor": "rgba(255, 255, 255, 0.8)",
                    "bordercolor": "rgba(0, 0, 0, 0.2)",
                    "borderwidth": 1
                }
            }

        except Exception as e:
            self._show_empty_plot(str(e))

    def _show_empty_plot(self, error=None):
        """Helper method to show empty plot state."""
        message = "No Email Statistics Available" if not error else f"Error: {error}"
        self.email_numbers_plot.data = [{
            "type": "bar",
            "x": ["No Data"],
            "y": [0],
            "name": "No Data"
        }]
        self.email_numbers_plot.layout.update({
            "title": message,
            "xaxis": {"title": None},
            "yaxis": {"title": "Number of Emails"},
            "showlegend": True,
            "margin": {"r": 100},  # Consistent margin
            "legend": {
                "yanchor": "top",
                "y": 1,
                "xanchor": "left",
                "x": 1.02
            }
        })
