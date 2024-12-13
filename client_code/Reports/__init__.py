# Reports Client-Side Code
from ._anvil_designer import ReportsTemplate
from anvil import *
import anvil.server
from datetime import datetime, timedelta

class Reports(ReportsTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.column_names = []
        self.user_values = []
        self._setup_initial_state()

    def _setup_initial_state(self):
        """Initialize the reports view with default settings."""
        # Set default date range (last 7 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        self.start_date_picker.date = start_date
        self.end_date_picker.date = end_date
        
        # Initial data load
        self.refresh_data()

    def refresh_data(self):
        """Fetch and display data based on current date range."""
        try:
            data = anvil.server.call(
                'get_call_data',
                self.start_date_picker.date,
                self.end_date_picker.date
            )
            
            if not self._validate_data(data):
                raise ValueError("Invalid data format received")
                
            self.column_names = data["columns"]
            self.user_values = data["values"]
            
            self._populate_numeric_columns()
            self._update_visualizations()
            
        except Exception as e:
            alert(f"Error refreshing data: {str(e)}")
            print(f"Error in refresh_data: {e}")

    def _validate_data(self, data):
        """Validate the structure of received data."""
        return (
            isinstance(data, dict) and
            "columns" in data and
            "values" in data and
            isinstance(data["columns"], list) and
            isinstance(data["values"], list) and
            all(isinstance(col, str) for col in data["columns"]) and
            all(isinstance(row, list) for row in data["values"])
        )

    def _populate_numeric_columns(self):
        """Populate dropdown with numeric column options."""
        try:
            numeric_columns = [
                col for col, val in zip(self.column_names, self.user_values[0])
                if isinstance(val, (int, float))
            ]
            self.data_column_selector.items = numeric_columns
            if numeric_columns:
                self.data_column_selector.selected_value = numeric_columns[0]
        except Exception as e:
            print(f"Error populating numeric columns: {e}")

    def _update_visualizations(self):
        """Update both plot and repeating panel."""
        if self.data_column_selector.selected_value:
            self._update_plot(self.data_column_selector.selected_value)
            self._update_repeating_panel()

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
        """Handle filter button click."""
        if not self.data_column_selector.selected_value:
            alert("Please select a data column")
            return
            
        self._update_visualizations()
