from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.server
import anvil.users
from anvil.tables import app_tables
from ..Reports import Reports
from ..Sales import Sales
from ..Admin import Admin
from datetime import datetime

class Frame(FrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        anvil.users.login_with_form()

    def refresh_button_click(self, **event_args):
        """Handle refresh button click to fetch call reports and email stats."""
        try:
            print("Refreshing data...")

            # Fetch call reports
            call_reports_result = anvil.server.call('fetch_call_reports')
            if call_reports_result:
                print("Call reports refreshed successfully.")
            else:
                print("No new call report data found.")

            # Fetch email stats
            email_stats = anvil.server.call('fetch_user_email_stats')
            print("Email Stats:")
            for stat in email_stats:
                print(stat)

            return {
                "success": True,
                "email_stats": email_stats,
                "call_reports_refreshed": call_reports_result
            }

        except Exception as e:
            print(f"Error refreshing data: {e}")
            return {"error": str(e)}

    def sales_page_link_click(self, **event_args):
        try:
            print("Switching to Sales page...")
            self.content_panel.clear()
            self.content_panel.add_component(Sales())
            self.sales_page_link.background = app.theme_colors['Primary Container']
            self.reports_page_link.background = "transparent"
            self.admin_page_link.background = "transparent"
        except Exception as e:
            print(f"Error loading Sales page: {e}")
            alert(f"Error loading Sales page: {e}")

    def reports_page_link_click(self, **event_args):
        try:
            print("Switching to Reports page...")
            self.content_panel.clear()  # Clear any existing components

            # Add the new Reports page
            print("Reports page initialized successfully.")
            self.content_panel.add_component(Reports())

            # Update UI link highlights
            self.reports_page_link.background = app.theme_colors['Primary Container']
            self.sales_page_link.background = "transparent"
            self.admin_page_link.background = "transparent"
            print("Reports page added to content panel.")

        except Exception as e:
            print(f"Error loading Reports page: {e}")
            alert(f"Error loading Reports page: {e}")

    def admin_page_link_click(self, **event_args):
        try:
            print("Switching to Admin page...")
            self.content_panel.clear()
            self.content_panel.add_component(Admin())
            self.admin_page_link.background = app.theme_colors['Primary Container']
            self.sales_page_link.background = "transparent"
            self.reports_page_link.background = "transparent"
        except Exception as e:
            print(f"Error loading Admin page: {e}")
            alert(f"Error loading Admin page: {e}")

    def signout_link_click(self, **event_args):
        alert("Sign out functionality not implemented yet.")

@anvil.server.callable
def fetch_call_reports():
    try:
        url = "https://api.example.com/call_reports"
        headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
        response = anvil.http.request(url, method="GET", headers=headers, json=True)

        if response.status_code == 200:
            data = response.get_bytes()
            update_call_statistics(data)
            return {"message": "Data refreshed successfully."}
        elif response.status_code == 404:
            return {"message": "No data found for the specified time frame."}
        else:
            raise Exception(f"Failed to fetch call data: {response.status_code} - {response.content}")
    except Exception as e:
        print(f"Error fetching call reports: {e}")
        raise

def update_call_statistics(data):
    today_date = datetime.utcnow().date()

    for item in data.get("items", []):
        user_id = item["userId"]
        user_name = item["userName"]
        data_values = item["dataValues"]

        # Check if a record exists for this user ID and today's date
        existing_row = app_tables.call_statistics.get(
            userId=user_id, reportDate=today_date
        )

        if existing_row:
            # Update the existing record
            existing_row.update(
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
            )
        else:
            # Add a new record
            app_tables.call_statistics.add_row(
                userId=user_id,
                userName=user_name,
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
                reportDate=today_date,
            )

def get_access_token():
    # Implement your logic to get access token
    pass

def fetch_user_stats(email, headers, today):
    try:
        url = f"https://api.example.com/user_stats?email={email}&date={today}"
        response = anvil.http.request(url, method="GET", headers=headers, json=True)
        if response.status_code == 200:
            return response.get_bytes()
        else:
            raise Exception(f"Failed to fetch user stats: {response.status_code} - {response.content}")
    except Exception as e:
        print(f"Error fetching user stats for {email}: {e}")
        raise

from ._anvil_designer import ReportsTemplate
from anvil import *
import anvil.server

class Reports(ReportsTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

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
