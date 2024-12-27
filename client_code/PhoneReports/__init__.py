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
from .. import theme_service

class PhoneReports(PhoneReportsTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Set table role and styling
        if hasattr(self, 'repeating_panel_1'):
            self.repeating_panel_1.role = 'table'
            self.repeating_panel_1.tag.style = """
                width: 100%;
                margin-top: 16px;
            """
        
        # Set default date range for calls
        self.end_date_picker.date = date.today()
        self.start_date_picker.date = date.today() - timedelta(days=7)
        
        # Initialize event handlers
        self._setup_event_handlers()
        
        # Single initial data refresh
        self.refresh_data()
    
    def _setup_event_handlers(self):
        """Set up all event handlers at once"""
        self.start_date_picker.set_event_handler('change', self.date_picker_change)
        self.end_date_picker.set_event_handler('change', self.date_picker_change)
        self.data_column_selector.set_event_handler('change', self.column_selector_change)

    def date_picker_change(self, **event_args):
        self.refresh_data()

    def column_selector_change(self, **event_args):
        if self.data_column_selector.selected_value:
            self._update_plot(self.data_column_selector.selected_value)
            self._update_repeating_panel()

    def refresh_data(self):
        """Fetch and display call data based on current date range."""
        try:
            with anvil.server.no_loading_indicator:
                data = anvil.server.call('get_call_data', 
                                       self.start_date_picker.date, 
                                       self.end_date_picker.date)
            
            if not data or "columns" not in data or "values" not in data:
                raise ValueError("Invalid data structure received")

            self.column_names = data["columns"]
            self.user_values = data["values"]
            self._process_data()
            
        except Exception as e:
            print(f"Error refreshing call data: {e}")
            alert(f"Error refreshing data: {e}")

    def _process_data(self):
        """Process the fetched data and update UI components"""
        try:
            # Process duration columns
            duration_columns = [col for col in self.column_names if 'duration' in col.lower()]
            for row in self.user_values:
                for col in duration_columns:
                    col_index = self.column_names.index(col)
                    if row[col_index] is not None:
                        row[col_index] = int(row[col_index] // 60000)

            # Update column selector with formatted titles
            numeric_columns = [
                col for i, col in enumerate(self.column_names)
                if all(isinstance(row[i], (int, float)) for row in self.user_values)
            ]
            
            if numeric_columns:
                # Create items list with formatted display names
                formatted_items = [
                    (self._format_title(col), col) for col in numeric_columns
                ]
                self.data_column_selector.items = formatted_items
                
                # Set selected value if none exists
                y_column = self.data_column_selector.selected_value or numeric_columns[0]
                self._update_plot(y_column)
                self._update_repeating_panel()
                
        except Exception as e:
            print(f"Error processing data: {e}")

    def _format_title(self, column_name):
        """Format column name for display in title"""
        # Split on camelCase
        words = ''.join(' ' + c if c.isupper() else c for c in column_name).strip()
        # Split on underscores and clean up
        words = ' ' .join(word.capitalize() for word in words.split('_'))
        return words

    def _update_plot(self, y_column):
        try:
            # Clear existing plot data and layout
            self.call_info_plot.data = []
            self.call_info_plot.layout = {}

            if "reportDate" not in self.column_names or y_column not in self.column_names:
                raise ValueError("Required columns missing")

            # Reset and set column values
            formatted_title = None
            y_column_value = None
            
            y_column_value = y_column  # Set new value
            formatted_title = self._format_title(y_column_value)  # Set new formatted title

            user_id_index = self.column_names.index('userId')
            user_name_index = self.column_names.index('userName')
            report_date_index = self.column_names.index('reportDate')
            y_column_index = self.column_names.index(y_column_value)

            grouped_data = {}
            user_labels = {}
            
            # Group data by user
            for row in self.user_values:
                user_id = row[user_id_index]
                if user_id not in grouped_data:
                    grouped_data[user_id] = {'x': [], 'y': []}
                    user_labels[user_id] = row[user_name_index]
                grouped_data[user_id]['x'].append(row[report_date_index].strftime('%Y-%m-%d'))
                grouped_data[user_id]['y'].append(row[y_column_index])

            # Create fresh traces
            traces = []
            for user_id, data in grouped_data.items():
                traces.append({
                    'x': data['x'],
                    'y': data['y'],
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': user_labels[user_id]
                })
            
            # Set complete fresh layout
            date_range = f"({self.start_date_picker.date} - {self.end_date_picker.date})"
            
            self.call_info_plot.data = traces
            self.call_info_plot.layout = {  # Complete layout reset
                'title': f"{formatted_title} {date_range}",
                'xaxis': {'title': None},
                'yaxis': {'title': formatted_title},
                'showlegend': True,
                'paper_bgcolor': theme_service.theme.get_color('Background'),
                'plot_bgcolor': theme_service.theme.get_color('Background'),
                'font': {'color': theme_service.theme.get_color('Text')},
            }

        except Exception as e:
            print(f"Error updating plot: {e}")
            self._show_empty_plot(str(e))

    def _show_empty_plot(self, error=None):
        """Helper method to show empty plot state."""
        message = "No Call Statistics Available" if not error else f"Error: {error}"
        self.call_info_plot.data = [{"type": "scatter", "x": ["No Data"], "y": [0]}]
        self.call_info_plot.layout = {
            "title": message,
            "xaxis": {"title": "Time"},
            "yaxis": {"title": "Value"},
            "showlegend": False,
        }

    def _update_repeating_panel(self):
        try:
            selected_users = [trace['name'] for trace in self.call_info_plot.data]
            user_name_index = self.column_names.index('userName')
            grouped_rows = {}

            # Consolidate data by user
            for row in self.user_values:
                user_name = row[user_name_index]
                if user_name in selected_users:
                    if user_name not in grouped_rows:
                        grouped_rows[user_name] = dict(zip(self.column_names, row))
                    else:
                        for i, col_name in enumerate(self.column_names):
                            if isinstance(row[i], (int, float)):
                                grouped_rows[user_name][col_name] += row[i]

            self.repeating_panel_1.items = list(grouped_rows.values())

        except Exception as e:
            print(f"Error updating repeating panel: {e}")

