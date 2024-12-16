from ._anvil_designer import B2bReportsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class B2bReports(B2bReportsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def b2b_metric_selector_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def b2b_start_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    pass

  def b2b_end_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    pass
