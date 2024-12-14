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
            # Configure global plot theme
            Plot.templates.default = {
                'layout': {
                    'paper_bgcolor': 'white',
                    'plot_bgcolor': 'rgba(0,0,0,0.02)',
                    'font': {'family': 'Inter, sans-serif', 'size': 12},
                    'margin': {'t': 32, 'r': 16, 'l': 64, 'b': 64},
                    'showlegend': True,
                    'legend': {'bgcolor': 'white', 'bordercolor': 'rgba(0,0,0,0.1)', 'borderwidth': 1},
                    'xaxis': {
                        'gridcolor': 'rgba(0,0,0,0.05)',
                        'linecolor': 'rgba(0,0,0,0.1)',
                        'tickfont': {'size': 10},
                        'showgrid': True
                    },
                    'yaxis': {
                        'gridcolor': 'rgba(0,0,0,0.05)',
                        'linecolor': 'rgba(0,0,0,0.1)',
                        'tickfont': {'size': 10},
                        'showgrid': True
                    }
                }
            }
            
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
