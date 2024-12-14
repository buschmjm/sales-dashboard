from ._anvil_designer import AdminTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Admin(AdminTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Apply table styling
        if hasattr(self, 'repeating_panel_1'):
            self.repeating_panel_1.role = 'table'
        
        self.repeating_panel_1.items = app_tables.users.search()