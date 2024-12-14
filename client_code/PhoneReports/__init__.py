# Reports Client-Side Code
from ._anvil_designer import PhoneReportsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, date

class PhoneReports(PhoneReportsTemplate):
    def __init__(self, **properties):
        # Initialize form and components
        self.init_components(**properties)

        # Set default date range for calls
        self.end_date_picker.date = date.today()  # Change to include today
        self.start_date_picker.date = date.today() - timedelta(days=7)  # Last 7 days

        # Set default date range for emails
        self.email_end_date.date = date.today()  # Change to include today
        self.email_start_date.date = date.today() - timedelta(days=7)  # Last 7 days

        # Set up email metrics dropdown
        self.email_metric_selector.items = [
            ('Total Emails', 'total'),
            ('Emails Received', 'inbound'),
            ('Emails Sent', 'outbound')
        ]
        self.email_metric_selector.selected_value = 'total'

        # Bind metric selector change event
        self.email_metric_selector.set_event_handler('change', self.email_metric_changed)

        # Bind change events to date pickers
        self.start_date_picker.set_event_handler('change', self.date_picker_change)
        self.end_date_picker.set_event_handler('change', self.date_picker_change)
        self.email_start_date.set_event_handler('change', self.email_date_change)
        self.email_end_date.set_event_handler('change', self.email_date_change)
        self.data_column_selector.set_event_handler('change', self.column_selector_change)

        self.refresh_data()
        self.refresh_email_data()

    def email_metric_changed(self, **event_args):
        """Handle metric selector change"""
        self.refresh_email_data()  # Refresh data when metric changes

    def date_picker_change(self, **event_args):
        """Handle call statistics date picker changes"""
        self.refresh_data()

    def email_date_change(self, **event_args):
        """Handle email statistics date picker changes"""
        self.refresh_email_data()

    def column_selector_change(self, **event_args):
        """Handle column selector changes"""
        if self.data_column_selector.selected_value:
            self._update_plot(self.data_column_selector.selected_value)
            self._update_repeating_panel()

    def refresh_data(self):
        """Fetch and display data based on current date range."""
        try:
            # Fetch data from the server
            data = anvil.server.call('get_call_data', self.start_date_picker.date, self.end_date_picker.date)

            # Debug: Inspect the fetched data
            print(f"Fetched data: {data}")

            # Validate data existence and structure
            if not data or "columns" not in data or "values" not in data:
                raise ValueError("Missing 'columns' or 'values' in the data.")

            # Validate the data structure
            if not isinstance(data.get("columns"), list):
                raise ValueError("Expected 'columns' to be a list of strings.")
            if not all(isinstance(col, str) for col in data["columns"]):
                raise ValueError("All column names must be strings.")

            if not isinstance(data.get("values"), list):
                raise ValueError("Expected 'values' to be a list of lists.")
            if not all(isinstance(row, list) for row in data["values"]):
                raise ValueError("Each row in 'values' must be a list.")

            # Store data as instance attributes
            self.column_names = data["columns"]
            self.user_values = data["values"]

            # Convert durations in milliseconds to minutes for relevant columns
            duration_columns = [
                col for col in self.column_names if 'duration' in col.lower()
            ]
            for row in self.user_values:
                for col in duration_columns:
                    col_index = self.column_names.index(col)
                    row[col_index] = int(row[col_index] // 60000)  # Ensure integer division and convert ms to minutes


            # Populate dropdown with numeric columns
            numeric_columns = [
                col for i, col in enumerate(self.column_names)
                if all(isinstance(row[i], (int, float)) for row in self.user_values)
            ]
            print(f"Numeric columns identified: {numeric_columns}")

            # Ensure dropdown items are tuples of hashable types
            self.data_column_selector.items = [(col, col) for col in numeric_columns if isinstance(col, str)]

            if not numeric_columns:
                alert("No numeric columns available for plotting. Please check the data.")
                self.data_column_selector.items = []  # Clear the dropdown if no numeric columns
                return

            # Update the plot and table data with the first selected column or volume
            y_column = self.data_column_selector.selected_value or ('volume' if 'volume' in numeric_columns else numeric_columns[0])
            self._update_plot(y_column)
            self._update_repeating_panel()

        except Exception as e:
            alert(f"Error initializing Reports page: {e}")
            print(f"Error initializing Reports page: {e}")

    def refresh_email_data(self):
        """Fetch and display email data based on current date range."""
        try:
            start_date = self.email_start_date.date
            end_date = self.email_end_date.date
            
            # Get statistics without forcing refresh every time
            data = anvil.server.call('get_email_stats', start_date, end_date)
            self._update_email_plot(data)
            
        except Exception as e:
            alert("Failed to refresh email data")
            print(f"Error: {e}")

    def _update_plot(self, y_column):
        """Helper function to update the plot."""
        try:
            print(f"Updating plot with y_column: {y_column}")
            print(f"Column names: {self.column_names}")
            print(f"User values: {self.user_values}")

            # Validate 'reportDate' and 'y_column' existence
            if 'reportDate' not in self.column_names:
                raise ValueError("Missing 'reportDate' column in data.")
            if y_column not in self.column_names:
                raise ValueError(f"Column '{y_column}' not found in data.")

            # Group data by userId and associate with userName for labels
            user_id_index = self.column_names.index('userId')
            user_name_index = self.column_names.index('userName')
            report_date_index = self.column_names.index('reportDate')
            y_column_index = self.column_names.index(y_column)

            grouped_data = {}
            user_labels = {}
            for row in self.user_values:
                user_id = row[user_id_index]
                user_name = row[user_name_index]
                report_date = row[report_date_index].strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
                y_value = row[y_column_index]

                if user_id not in grouped_data:
                    grouped_data[user_id] = {'x': [], 'y': []}
                    user_labels[user_id] = user_name  # Map userId to userName
                grouped_data[user_id]['x'].append(report_date)
                grouped_data[user_id]['y'].append(y_value)

            # Create a line for each userId with userName as the label
            self.call_info_plot.data = [
                {
                    'x': grouped_data[user_id]['x'],
                    'y': grouped_data[user_id]['y'],
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': user_labels[user_id],  # Use userName for the legend
                }
                for user_id in grouped_data
            ]

        except Exception as e:
            alert(f"Error updating plot: {e}")
            print(f"Error updating plot: {e}")

    def _update_email_plot(self, data):
        """Update the email statistics plot with a grouped bar chart."""
        try:
            if not data or 'users' not in data or 'metrics' not in data:
                self._show_empty_plot()
                return
            
            users = data['users']
            if users == ['No Data']:
                self._show_empty_plot()
                return

            # Get selected metric and update plot efficiently
            metric = self.email_metric_selector.selected_value or 'total'
            metric_name = {'total': 'Total', 'inbound': 'Received', 'outbound': 'Sent'}[metric]
            
            # Create plot with minimal operations
            self.email_numbers_plot.data = [{
                'type': 'bar',
                'x': users,
                'y': data['metrics'][metric],
                'name': f'{metric_name} Emails'
            }]

            # Update only necessary layout properties
            self.email_numbers_plot.layout.update({
                'title': f'{metric_name} Emails ({self.email_start_date.date} - {self.email_end_date.date})',
                'xaxis': {'tickangle': 45},
                'height': 600
            })

        except Exception as e:
            self._show_empty_plot()

    def _show_empty_plot(self, error=None):
        """Helper method to show empty plot state."""
        message = 'No Email Statistics Available' if not error else f'Error: {error}'
        self.email_numbers_plot.data = [{
            'type': 'bar',
            'x': ['No Data'],
            'y': [0]
        }]
        self.email_numbers_plot.layout.update({
            'title': message,
            'xaxis': {'title': 'Users'},
            'yaxis': {'title': 'Number of Emails'},
            'showlegend': False
        })

    def _update_repeating_panel(self):
        """Update the repeating_panel_1 with consolidated filtered data."""
        try:
            selected_users = [trace['name'] for trace in self.call_info_plot.data]
            print(f"Selected users for repeating panel: {selected_users}")

            # Filter and consolidate rows by userName
            user_name_index = self.column_names.index('userName')
            grouped_rows = {}

            for row in self.user_values:
                user_name = row[user_name_index]
                if user_name in selected_users:
                    if user_name not in grouped_rows:
                        grouped_rows[user_name] = dict(zip(self.column_names, row))
                    else:
                        # Consolidate numeric fields
                        for i, col_name in enumerate(self.column_names):
                            if isinstance(row[i], (int, float)):
                                grouped_rows[user_name][col_name] += row[i]

            # Convert grouped_rows to a list of dictionaries
            consolidated_rows = list(grouped_rows.values())

            # Debug consolidated rows
            print(f"Consolidated rows for repeating panel: {consolidated_rows}")

            # Display consolidated data in the repeating_panel_1
            self.repeating_panel_1.items = consolidated_rows

        except Exception as e:
            alert(f"Error updating repeating panel: {e}")
            print(f"Error updating repeating panel: {e}")
