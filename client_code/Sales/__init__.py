from ._anvil_designer import SalesTemplate
from anvil import *
from ..theme_service import AppTheme

class Sales(SalesTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.refresh_theme()

    def refresh_theme(self):
        colors = AppTheme.get_colors()  # No argument needed
        self.background = colors['Background']