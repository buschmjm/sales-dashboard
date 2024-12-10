from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Reports import Reports
from ..Sales import Sales

class Frame(FrameTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Add a refresh button
        self.refresh_button = Button(text="Refresh", align="right", role="primary-color")
        self.refresh_button.set_event_handler("click", self.refresh_button_click)
        self.add_component(self.refresh_button, slot="top-right")

        Plot.templates.default = "rally"
        self.content_panel.add_component(Sales())
        self.sales_page_link.background = app.theme_colors['Primary Container']

    def refresh_button_click(self, **event_args):
        """This method is called when the refresh button is clicked"""
        try:
            # Call the manually triggered function
            result = anvil.server.call('fetch_call_reports')
            if result:
                alert("Data refreshed successfully!", title="Success")
            else:
                alert("No new data found.", title="Info")
        except Exception as e:
            alert(f"Failed to refresh data: {e}", title="Error")

    def sales_page_link_click(self, **event_args):
        self.content_panel.clear()
        self.content_panel.add_component(Sales())
        self.sales_page_link.background = app.theme_colors['Primary Container']
        self.reports_page_link.background = "transparent"

    def reports_page_link_click(self, **event_args):
        self.content_panel.clear()
        self.content_panel.add_component(Reports())
        self.reports_page_link.background = app.theme_colors['Primary Container']
        self.sales_page_link.background = "transparent"

    def signout_link_click(self, **event_args):
        """Placeholder method for the sign-out link click event."""
        alert("Sign out functionality not implemented yet.")
