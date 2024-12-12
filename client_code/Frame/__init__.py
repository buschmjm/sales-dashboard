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
            email_stats = anvil.server.call('get_email_stats')
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
