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

    # Add the refresh button to the top-right of the form
    self.refresh_button = Button(text="Refresh", align="right", role="primary-color")
    self.refresh_button.set_event_handler("click", self.refresh_button_click)
    self.add_component(self.refresh_button, slot="top-right")

    # Set the Plotly plots template to match the theme of the app
    Plot.templates.default = "rally"

    # When the app starts up, the Sales form will be added to the page
    self.content_panel.add_component(Sales())

    # Change the color of the sales_page_link to indicate that the Sales page has been selected
    self.sales_page_link.background = app.theme_colors['Primary Container']

  def refresh_button_click(self, **event_args):
    """This method is called when the refresh button is clicked"""
    try:
      # Call the fetch_call_reports function from the server
      result = anvil.server.call('fetch_call_reports_requests')
      alert("Data refreshed successfully!", title="Success")
    except Exception as e:
      alert(f"Failed to refresh data: {e}", title="Error")

  def sales_page_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    # Clear the content panel and add the Sales Form
    self.content_panel.clear()
    self.content_panel.add_component(Sales())
    # Change the color of the sales_page_link to indicate that the Sales page has been selected
    self.sales_page_link.background = app.theme_colors['Primary Container']
    self.reports_page_link.background = "transparent"

  def reports_page_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    # Clear the content panel and add the Reports Form
    self.content_panel.clear()
    self.content_panel.add_component(Reports())
    # Change the color of the sales_page_link to indicate that the Reports page has been selected
    self.reports_page_link.background = app.theme_colors['Primary Container']
    self.sales_page_link.background = "transparent"