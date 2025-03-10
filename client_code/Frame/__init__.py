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
            
            # Check admin status and setup navigation accordingly
            self.is_admin = self._check_admin_status()
            if not self.is_admin:
                self.admin_page_link.visible = False
                
            self._setup_navigation()
            
        except Exception as e:
            print(f"Error initializing Frame: {e}")
            alert(f"Error initializing Frame: {e}")

    def _check_admin_status(self):
        """Check if current user has admin privileges"""
        try:
            current_user = anvil.users.get_user()
            user_row = app_tables.users.get(email=current_user['email'])
            return user_row['Admin'] if user_row else False
        except Exception as e:
            print(f"Error checking admin status: {e}")
            return False

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
        self.sales_page_link.background = app.theme_colors['Primary Container']
        self.sales_page_link.foreground = 'white'

    def _switch_page(self, page_name, component):
        # Don't allow non-admins to access admin page
        if page_name == 'admin' and not self.is_admin:
            self._switch_page('sales', Sales())
            alert("You don't have permission to access the admin page.")
            return
            
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
            active_link.background = app.theme_colors['Primary Container']
            active_link.foreground = 'white'

    def refresh_button_click(self, **event_args):
        """Handle refresh button click - triggers database refresh APIs."""
        try:
            # Show loading indicator to user
            notification = Notification("Refreshing data...", timeout=None)
            notification.show()
            
            # Call APIs sequentially and capture results
            call_reports_refreshed = anvil.server.call('fetch_call_reports')
            
            try:
                email_stats = anvil.server.call('fetch_user_email_stats')
                email_stats_status = 'Updated' if email_stats and isinstance(email_stats, list) else 'No new data'
            except Exception as email_error:
                print(f"Error in fetch_user_email_stats: {email_error}")
                email_stats_status = 'Failed to update'
            
            # Force recalculation of averages
            averages_recalculated = anvil.server.call('recalculate_todays_averages')
            
            # Log results
            print("Refresh results:")
            print(f"- Call reports: {'Updated' if call_reports_refreshed else 'No new data'}")
            print(f"- Email stats: {email_stats_status}")
            print(f"- Averages: {'Recalculated' if averages_recalculated else 'Failed to recalculate'}")
            
            # Hide loading indicator
            notification.hide()
            
            # Show completion notification
            Notification("Data refresh complete.", timeout=3).show()
            
            # Refresh current page if it's the Sales page
            if self.current_page == 'sales':
                current_content = self.content_panel.get_components()[0]
                if hasattr(current_content, 'refresh_data'):
                    current_content.refresh_data()
            
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
      """This method is called when the button is clicked"""
      pass

    def light_mode_click(self, **event_args):
      """This method is called when the button is clicked"""
      pass

