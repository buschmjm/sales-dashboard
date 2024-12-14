from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Reports import Reports
from ..Sales import Sales
from ..Admin import Admin
from ..ReportsInnerFrame import ReportsInnerFrame  # Add this import

anvil.users.login_with_form()

class Frame(FrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        try:
            self.refresh_button = Button(text="Refresh", align="right", role="primary-color")
            self.refresh_button.set_event_handler("click", self.refresh_button_click)
            self.add_component(self.refresh_button, slot="top-right")

            Plot.templates.default = "rally"

            print("Loading Sales page...")
            self.content_panel.add_component(Sales())
            self.sales_page_link.background = app.theme_colors['Primary Container']

        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

    def refresh_button_click(self, **event_args):
        """Handle refresh button click - only triggers database refresh APIs."""
        try:
            # Show loading indicator to user
            Notification("Refreshing data...").show()
            
            # Call APIs sequentially and capture results
            call_reports_refreshed = anvil.server.call('fetch_call_reports')
            email_stats_refreshed = anvil.server.call('fetch_user_email_stats')
            
            # Log results without affecting UI
            print("Refresh results:")
            print(f"- Call reports: {'Updated' if call_reports_refreshed else 'No new data'}")
            print(f"- Email stats: {'Updated' if email_stats_refreshed else 'No new data'}")
            
            # Notify user of completion
            Notification("Data refresh complete.").show()
            
        except Exception as e:
            print(f"Error during data refresh: {e}")
            alert("Failed to refresh data. Please try again.")

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
            self.content_panel.clear()

            # Add the ReportsInnerFrame instead of Reports
            reports_frame = ReportsInnerFrame()
            self.content_panel.add_component(reports_frame)

            # Update UI link highlights
            self.reports_page_link.background = app.theme_colors['Primary Container']
            self.sales_page_link.background = "transparent"
            self.admin_page_link.background = "transparent"
            print("Reports inner frame added to content panel.")

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
