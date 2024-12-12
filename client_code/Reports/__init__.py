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
        self.init_components(**properties)

        # Initialize Date Pickers
        self.end_date_picker.date = date.today() - timedelta(days=1)
        self.start_date_picker.date = date.today() - timedelta(days=15)

        # Initialize Plot and Dropdown to avoid NoneType errors
        self.call_info_plot.data = []  # Empty plot to start
        self.data_column_selector.items = []  # Empty dropdown to start

        # Call server to fetch initial data
        self.load_data()
    
    def load_data(self):
        try:
            # Call the server to fetch data
            self.queryData = list(anvil.server.call(
                'get_call_data', self.start_date_picker.date, self.end_date_picker.date
            ))

            # Ensure there is data
            if not self.queryData:
                alert("No data available for the selected date range.")
                return
            
            # Populate Dropdown with numeric columns
            row = self.queryData[0]
            self.data_column_selector.items = [(col, col) for col, value in row.items() if isinstance(value, (int, float))]

            # Default Y-axis column
            y_column = 'volume'

            # Initialize Plot
            self.call_info_plot.data = [
                {
                    'x': [row['reportDate'] for row in self.queryData],
                    'y': [row[y_column] for row in self.queryData if y_column in row],
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': f"{y_column} over time",
                }
            ]
        except Exception as e:
            print(f"Error loading data: {e}")
            alert("Failed to load data. Please try again.")

    def filter_button_click(self, **event_args):
        # Update the plot dynamically
        try:
            y_column = self.data_column_selector.selected_value
            if not y_column:
                alert("Please select a column.")
                return

            self.call_info_plot.data = [
                {
                    'x': [row['reportDate'] for row in self.queryData],
                    'y': [row[y_column] for row in self.queryData if y_column in row],
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': f"{y_column} over time",
                }
            ]
        except Exception as e:
            print(f"Error updating plot: {e}")
            alert("Failed to update plot. Please try again.")