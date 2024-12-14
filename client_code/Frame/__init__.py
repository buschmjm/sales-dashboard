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
        # Initialize navigation state
        self._current_page = None
        self.init_components(**properties)
        self.content_panel.role = 'none'

        try:
            # Setup refresh button
            self.refresh_button = Button(text="Refresh", align="right", role="primary-color")
            self.refresh_button.set_event_handler("click", self.refresh_button_click)
            self.add_component(self.refresh_button, slot="top-right")

            # Set plot template
            Plot.templates.default = "rally"

            # Setup navigation styling
            for nav in [self.sales_page_link, self.reports_page_link, self.admin_page_link]:
                nav.background = "transparent"
                nav.hover_background = app.theme_colors['Surface Variant']
                nav.foreground = "black"

            # Initial page load without triggering navigation events
            self._load_page('sales', Sales())
            
        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

    def _load_page(self, page_name, component):
        """Helper method to load pages without triggering unnecessary updates"""
        if self._current_page != page_name:
            self._current_page = page_name
            self.content_panel.clear()
            self.content_panel.add_component(component)
            self._update_nav_highlights(page_name)

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
            self._load_page('sales', Sales())
        except Exception as e:
            print(f"Error loading Sales page: {e}")
            alert(f"Error loading Sales page: {e}")

    def reports_page_link_click(self, **event_args):
        try:
            self._load_page('reports', ReportsInnerFrame())
        except Exception as e:
            print(f"Error loading Reports page: {e}")
            alert(f"Error loading Reports page: {e}")

    def admin_page_link_click(self, **event_args):
        try:
            self._load_page('admin', Admin())
        except Exception as e:
            print(f"Error loading Admin page: {e}")
            alert(f"Error loading Admin page: {e}")

    def signout_link_click(self, **event_args):
        alert("Sign out functionality not implemented yet.")
