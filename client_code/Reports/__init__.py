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

            # Determine default y-axis column
            y_column = 'volume' if 'volume' in numeric_columns else numeric_columns[0]

            # Set initial plot data
            self._update_plot(y_column)

        except Exception as e:
            alert(f"Error initializing Reports page: {e}")
            print(f"Error initializing Reports page: {e}")

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

            self.call_info_plot.data = [
                {
                    'x': [row[self.column_names.index('reportDate')] for row in self.user_values],
                    'y': [row[self.column_names.index(y_column)] for row in self.user_values],
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': f"{y_column} over time",
                }
            ]
        except Exception as e:
            alert(f"Error updating plot: {e}")
            print(f"Error updating plot: {e}")

    def filter_button_click(self, **event_args):
        """Handle filter button click to update the plot."""
        y_column = self.data_column_selector.selected_value

        if not y_column:
            alert("Please select a column.")
            return

        self._update_plot(y_column)