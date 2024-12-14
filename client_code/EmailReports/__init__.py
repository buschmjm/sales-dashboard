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

        # Set up email metrics dropdown
        self.email_metric_selector.items = [
            ('Total Emails', 'total'),
            ('Emails Received', 'inbound'),
            ('Emails Sent', 'outbound')
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
        """Update the email statistics plot with a grouped bar chart."""
        try:
            if not data or "users" not in data or "metrics" not in data:
                self._show_empty_plot()
                return

            users = data["users"]
            if users == ["No Data"]:
                self._show_empty_plot()
                return

            # Get selected metric and update plot efficiently
            metric = self.email_metric_selector.selected_value or "total"
            metric_name = {"total": "Total", "inbound": "Received", "outbound": "Sent"}[
                metric
            ]

            # Create plot with consistent styling
            self.email_numbers_plot.data = [{
                "type": "bar",
                "x": users,
                "y": data["metrics"][metric],
                "name": f"{metric_name} Emails",
                "marker": {
                    "color": [
                        app.theme_colors[f'Primary {(i%3)+1}'] 
                        for i in range(len(users))
                    ],
                    "opacity": 0.9,
                    "line": {
                        "color": "white",
                        "width": 1
                    }
                },
                "hovertemplate": "%{x}<br>%{y} Emails<extra></extra>"
            }]

            # Modern layout with consistent styling
            self.email_numbers_plot.layout.update({
                "height": 400,
                "title": {
                    "text": f"{metric_name} Emails ({self.email_start_date.date} - {self.email_end_date.date})",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 16}
                },
                "xaxis": {
                    "title": None,
                    "tickangle": 45,
                    "showline": True
                },
                "yaxis": {
                    "title": "Number of Emails",
                    "showline": True,
                    "zeroline": True,
                    "zerolinecolor": "rgba(0,0,0,0.1)"
                },
                "bargap": 0.3,
                "hoverlabel": {"bgcolor": "white"},
                "hovermode": "x unified"
            })

        except Exception as e:
            self._show_empty_plot()

    def _show_empty_plot(self, error=None):
        """Helper method to show empty plot state."""
        message = "No Email Statistics Available" if not error else f"Error: {error}"
        self.email_numbers_plot.data = [{"type": "bar", "x": ["No Data"], "y": [0]}]
        self.email_numbers_plot.layout.update(
            {
                "title": message,
                "xaxis": {"title": "Users"},
                "yaxis": {"title": "Number of Emails"},
                "showlegend": False,
            }
        )
