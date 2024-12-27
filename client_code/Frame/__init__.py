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
from .. import theme_service
from .. import theme_utils

anvil.users.login_with_form()

class Frame(FrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.is_dark_mode = False
        self._update_theme_buttons()
        self._apply_theme()

        try:
            # Minimal configuration
            self.content_panel.role = 'none'
            
            # Simple button setup
            self.refresh_button = Button(
                text="Refresh",
                role="primary-color"
            )
            self.refresh_button.set_event_handler("click", self.refresh_button_click)
            self.add_component(self.refresh_button, slot="top-right")

            Plot.templates.default = "rally"
            self._setup_navigation()
            
        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

    @staticmethod
    def get_current_theme():
        """Get the current theme colors. Called by child components."""
        if not hasattr(Frame, '_current_theme'):
            Frame._current_theme = theme_utils.theme.get_colors(False)  # Default to light theme
        return Frame._current_theme

    def _setup_navigation(self):
        """Initialize navigation state and styling"""
        # Set initial states
        self.current_page = 'sales'
        self.content_panel.add_component(Sales())
        
        # Configure navigation links
        nav_links = [self.sales_page_link, self.reports_page_link, self.admin_page_link]
        for link in nav_links:
            link.background = 'transparent'
            link.foreground = 'black'
        
        # Set initial active state
        self.sales_page_link.background = theme_service.theme.get_color('Primary Container')
        self.sales_page_link.foreground = 'white'

    def _switch_page(self, page_name, component):
        if getattr(self, 'current_page', None) != page_name:
            self.current_page = page_name
            self.content_panel.clear()
            self.content_panel.add_component(component)
            
            # Reset all navigation backgrounds
            for link in [self.sales_page_link, self.reports_page_link, self.admin_page_link]:
                link.background = 'transparent'
                link.foreground = 'black'
            
            # Set active link
            active_link = getattr(self, f"{page_name}_page_link")
            active_link.background = theme_service.theme.get_color('Primary Container')
            active_link.foreground = 'white'

    def refresh_button_click(self, **event_args):
        """Handle refresh button click - only triggers database refresh APIs."""
        try:
            # Show loading indicator to user
            Notification("Refreshing data...").show()
            
            # Call APIs sequentially and capture results
            call_reports_refreshed = anvil.server.call('fetch_call_reports')
            
            try:
                email_stats = anvil.server.call('fetch_user_email_stats')
                email_stats_status = 'Updated' if email_stats and isinstance(email_stats, list) else 'No new data'
            except Exception as email_error:
                print(f"Error in fetch_user_email_stats: {email_error}")
                email_stats_status = 'Failed to update'
            
            # Log results without affecting UI
            print("Refresh results:")
            print(f"- Call reports: {'Updated' if call_reports_refreshed else 'No new data'}")
            print(f"- Email stats: {email_stats_status}")
            
            # Notify user of completion
            Notification("Data refresh complete.").show()
            
        except Exception as e:
            print(f"Error during data refresh: {e}")
            alert("Failed to refresh data. Please try again.")

    def sales_page_link_click(self, **event_args):
        """Handle sales page navigation"""
        self._switch_page('sales', Sales())

    def reports_page_link_click(self, **event_args):
        """Handle reports page navigation"""
        self._switch_page('reports', ReportsInnerFrame())

    def admin_page_link_click(self, **event_args):
        """Handle admin page navigation"""
        self._switch_page('admin', Admin())

    def signout_link_click(self, **event_args):
        alert("Sign out functionality not implemented yet.")

    def dark_mode_click(self, **event_args):
        """Switch to dark theme"""
        self.is_dark_mode = True
        self._update_theme_buttons()
        self._apply_theme()

    def light_mode_click(self, **event_args):
        """Switch to light theme"""
        self.is_dark_mode = False
        self._update_theme_buttons()
        self._apply_theme()

    def _update_theme_buttons(self):
        """Update the visual state of theme buttons"""
        Frame._current_theme = theme_utils.theme.get_colors(self.is_dark_mode)
        colors = Frame._current_theme
        button_colors = colors['Button']
        
        # Light mode button
        self.light_mode.background = button_colors['Active'] if not self.is_dark_mode else 'transparent'
        self.light_mode.foreground = button_colors['Text'] if not self.is_dark_mode else button_colors['Text Inactive']
        
        # Dark mode button
        self.dark_mode.background = button_colors['Active'] if self.is_dark_mode else 'transparent'
        self.dark_mode.foreground = button_colors['Text'] if self.is_dark_mode else button_colors['Text Inactive']

    def _apply_theme(self):
        """Apply the current theme to all components"""
        colors = theme_utils.theme.get_colors(self.is_dark_mode)
        
        self.content_panel.background = colors['Background']
        self.sidebar_panel.background = colors['Surface']
        
        for nav in [self.sales_page_link, self.reports_page_link, self.admin_page_link]:
            nav.foreground = colors['Text']

