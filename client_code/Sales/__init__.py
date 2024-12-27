from ._anvil_designer import SalesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..theme_manager import ThemeManager

class Sales(SalesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.refresh_theme()

  def refresh_theme(self):
    """Update component colors based on current theme"""
    colors = ThemeManager.get_theme()
    self.background = colors['Background']
    # Update other components as needed