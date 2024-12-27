from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js
from ..Sales import Sales
from ..Admin import Admin
from ..ReportsInnerFrame import ReportsInnerFrame

anvil.users.login_with_form()

class Frame(FrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
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
            
            # Initialize theme
            self.current_theme = 'light'
            self._apply_theme(self.current_theme)
            
        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

    def _setup_navigation(self):
        """Initialize navigation state and styling"""
        # Set initial states
        self.current_page = 'sales'
        self.content_panel.add_component(Sales())
        
        # Configure navigation links with theme variables
        nav_links = [self.sales_page_link, self.reports_page_link, self.admin_page_link]
        for link in nav_links:
            link.background = 'transparent'
            link.foreground = 'var(--text-color)'
        
        # Set initial active state using theme variables
        self.sales_page_link.background = 'var(--primary-color)'
        self.sales_page_link.foreground = 'var(--background-color)'

    def _switch_page(self, page_name, component):
        if getattr(self, 'current_page', None) != page_name:
            self.current_page = page_name
            self.content_panel.clear()
            self.content_panel.add_component(component)
            
            # Reset all navigation backgrounds using theme variables
            for link in [self.sales_page_link, self.reports_page_link, self.admin_page_link]:
                link.background = 'transparent'
                link.foreground = 'var(--text-color)'
            
            # Set active link using theme variables
            active_link = getattr(self, f"{page_name}_page_link")
            active_link.background = 'var(--primary-color)'
            active_link.foreground = 'var(--background-color)'

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
        """Handle dark mode button click"""
        self._apply_theme('dark')

    def light_mode_click(self, **event_args):
        """Handle light mode button click"""
        self._apply_theme('light')

    def _apply_theme(self, theme):
        """Apply the selected theme to the application"""
        try:
            # Update root element's data-theme attribute via JavaScript
            js_code = f"""
            (function() {{
                document.documentElement.setAttribute('data-theme', '{theme}');
            }})();
            """
            anvil.js.window.eval(js_code)
            
            # Store current theme
            self.current_theme = theme
            
            # Update button states using theme variables
            if theme == 'light':
                self.light_mode.background = 'var(--primary-color)'
                self.light_mode.foreground = 'var(--background-color)'
                self.dark_mode.background = 'transparent'
                self.dark_mode.foreground = 'var(--text-color)'
            else:
                self.dark_mode.background = 'var(--primary-color)'
                self.dark_mode.foreground = 'var(--background-color)'
                self.light_mode.background = 'transparent'
                self.light_mode.foreground = 'var(--text-color)'
            
            # Update content panel and other elements
            self.content_panel.background = 'var(--background-color)'
            self.content_panel.foreground = 'var(--text-color)'
            
            # Save user preference
            anvil.server.call('save_user_theme_preference', theme)
            
        except Exception as e:
            print(f"Error applying theme: {str(e)}")
            print(f"Full error details: {repr(e)}")

