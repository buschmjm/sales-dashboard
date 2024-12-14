from ._anvil_designer import ReportsInnerFrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReportsInnerFrame(ReportsInnerFrameTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def b2b_nav_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def email_nav_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def phone_nav_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
