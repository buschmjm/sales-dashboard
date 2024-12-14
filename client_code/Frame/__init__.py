from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Sales import Sales
from ..Admin import Admin
from ..ReportsInnerFrame import ReportsInnerFrame

anvil.users.login_with_form()

class Frame(FrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Add this line to remove any theme-based spacing
        self.content_panel.role = 'none'

        try:
            self.refresh_button = Button(text="Refresh", align="right", role="primary-color")
            self.refresh_button.set_event_handler("click", self.refresh_button_click)
            self.add_component(self.refresh_button, slot="top-right")

            Plot.templates.default = "rally"

            # Enhanced hover effects for navigation links
            for nav in [self.sales_page_link, self.reports_page_link, self.admin_page_link]:
                nav.background = "transparent"
                nav.hover_background = app.theme_colors['Surface Variant']
                nav.foreground = "black"  # Default text color

            # Set initial active state
            print("Loading Sales page...")
            self.content_panel.add_component(Sales())
            self._update_nav_highlights('sales')

        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

    def _update_nav_highlights(self, active_page):
        """Helper to update navigation highlighting"""
        # Reset all to default state
        for nav in [self.sales_page_link, self.reports_page_link, self.admin_page_link]:
            nav.background = "transparent"
            nav.foreground = "black"
        
        # Set active state
        active_link = getattr(self, f"{active_page}_page_link")
        active_link.background = app.theme_colors['Primary Container']
        active_link.foreground = "white"

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
            self._update_nav_highlights('sales')
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

            self._update_nav_highlights('reports')
            print("Reports inner frame added to content panel.")

        except Exception as e:
            print(f"Error loading Reports page: {e}")
            alert(f"Error loading Reports page: {e}")

    def admin_page_link_click(self, **event_args):
        try:
            print("Switching to Admin page...")
            self.content_panel.clear()
            self.content_panel.add_component(Admin())
            self._update_nav_highlights('admin')
        except Exception as e:
            print(f"Error loading Admin page: {e}")
            alert(f"Error loading Admin page: {e}")

    def signout_link_click(self, **event_args):
        alert("Sign out functionality not implemented yet.")
