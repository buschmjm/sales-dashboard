# Reports Client-Side Code
from ._anvil_designer import ReportsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, date

class Reports(ReportsTemplate):
    def __init__(self, **properties):
        # Initialize form and components
        self.init_components(**properties)

        # Set default date range
        self.end_date_picker.date = date.today() - timedelta(days=1)
        self.start_date_picker.date = date.today() - timedelta(days=15)

        self.refresh_data()

    def refresh_data(self):
        """Fetch and display data based on current date range."""
        try:
            # Fetch data from the server
            data = anvil.server.call('get_call_data', self.start_date_picker.date, self.end_date_picker.date)

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

            # Debugging: Print count only
            print(f"Number of rows fetched: {len(self.user_values)}")

            # Populate dropdown and update visuals
            self._populate_numeric_columns()
            self._update_plot(self.data_column_selector.selected_value or self._get_default_column())
            self._update_repeating_panel()

        except Exception as e:
            alert(f"Error refreshing Reports page: {e}")
            print(f"Error refreshing Reports page: {e}")

    def _populate_numeric_columns(self):
        """Populate dropdown with numeric columns."""
        numeric_columns = [
            col for i, col in enumerate(self.column_names)
            if all(isinstance(row[i], (int, float)) for row in self.user_values)
        ]
        print(f"Numeric columns identified: {numeric_columns}")
        self.data_column_selector.items = [(col, col) for col in numeric_columns]

    def _get_default_column(self):
        """Get default column for visualization."""
        return 'volume' if 'volume' in self.column_names else self.column_names[0]

    def _update_plot(self, y_column):
        """Helper function to update the plot."""
        try:
            print(f"Updating plot with y_column: {y_column}")

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

    def _update_repeating_panel(self):
        """Update the repeating_panel_1 with consolidated filtered data."""
        try:
            selected_users = [trace['name'] for trace in self.call_info_plot.data]
            print(f"Number of selected users for repeating panel: {len(selected_users)}")

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

            # Debugging: Print count only
            print(f"Number of consolidated rows: {len(consolidated_rows)}")

            # Display consolidated data in the repeating_panel_1
            self.repeating_panel_1.items = consolidated_rows

        except Exception as e:
            alert(f"Error updating repeating panel: {e}")
            print(f"Error updating repeating panel: {e}")

    def filter_button_click(self, **event_args):
        """Handle filter button click to update the plot, table, and fetch email stats."""
        y_column = self.data_column_selector.selected_value

        if not y_column:
            alert("Please select a column.")
            return

        # Update plot and table
        self._update_plot(y_column)
        self._update_repeating_panel()

        # Fetch email stats from the server
        try:
            email_stats = anvil.server.call('fetch_user_email_stats')
            print(f"Number of email stats fetched: {len(email_stats)}")
        except Exception as e:
            print(f"Error fetching email stats: {e}")
