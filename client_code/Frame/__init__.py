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
    # Class-level theme definitions
    light_theme = {
      'Primary Container': '#007AFF',
      'Background': '#FFFFFF',
      'Surface': '#F5F5F5',
      'Text': '#000000',
      'Secondary Text': '#666666'
    }
    
    dark_theme = {
      'Primary Container': '#0A84FF',
      'Background': '#000000',
      'Surface': '#1C1C1E',
      'Text': '#FFFFFF',
      'Secondary Text': '#EBEBF5'
    }
    
    # Class-level current theme reference
    current_theme = dict(light_theme)

    def __init__(self, **properties):
        # Make theme globally accessible
        app.theme_colors = self.current_theme
        
        # Initialize components
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
            
            self._update_theme_buttons()
            self._apply_theme()
            
        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

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
        self.sales_page_link.background = self.current_theme['Primary Container']
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
            active_link.background = self.current_theme['Primary Container']
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
        self.current_theme.clear()
        self.current_theme.update(self.dark_theme)
        self._update_theme_buttons()
        self._apply_theme()

    def light_mode_click(self, **event_args):
        """Switch to light theme"""
        self.current_theme.clear()
        self.current_theme.update(self.light_theme)
        self._update_theme_buttons()
        self._apply_theme()

    def _update_theme_buttons(self):
        """Update the visual state of theme buttons"""
        is_light = self.current_theme == self.light_theme
        
        # Light mode button
        self.light_mode.background = self.light_theme['Primary Container'] if is_light else 'transparent'
        self.light_mode.foreground = '#FFFFFF' if is_light else '#000000'
        
        # Dark mode button
        self.dark_mode.background = self.dark_theme['Primary Container'] if not is_light else 'transparent'
        self.dark_mode.foreground = '#FFFFFF' if not is_light else '#000000'

    def _apply_theme(self):
        """Apply the current theme to all components"""
        # Update main container backgrounds
        self.content_panel.background = self.current_theme['Background']
        self.sidebar_panel.background = self.current_theme['Surface']
        
        # Update text colors for navigation links
        for nav in [self.home_link, self.sales_link, self.reports_link, self.admin_link]:
            nav.foreground = self.current_theme['Text']

