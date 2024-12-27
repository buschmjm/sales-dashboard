from ._anvil_designer import SalesTemplate
from anvil import *
from ..utils.theme import Theme

class Sales(SalesTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.refresh_theme()

    def refresh_theme(self):
        colors = Theme.get_colors()
        self.background = colors['Background']