from ._anvil_designer import SalesTemplate
from anvil import *
from ..common.theme import AppTheme

class Sales(SalesTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.refresh_theme()

    def refresh_theme(self):
        colors = AppTheme.get_colors()
        self.background = colors['Background']