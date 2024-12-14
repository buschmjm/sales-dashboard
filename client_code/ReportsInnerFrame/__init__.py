from ._anvil_designer import ReportsInnerFrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..PhoneReports import PhoneReports
from ..EmailReports import EmailReports
from ..B2bReports import B2bReports


class ReportsInnerFrame(ReportsInnerFrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Load PhoneReports by default
        self.content_panel.add_component(PhoneReports())
        self.phone_nav.background = app.theme_colors['Primary Container']

    def phone_nav_click(self, **event_args):
        """Handle phone reports navigation"""
        self.content_panel.clear()
        self.content_panel.add_component(PhoneReports())
        self._update_nav_highlights('phone')

    def email_nav_click(self, **event_args):
        """Handle email reports navigation"""
        self.content_panel.clear()
        self.content_panel.add_component(EmailReports())
        self._update_nav_highlights('email')

    def b2b_nav_click(self, **event_args):
        """Handle B2B reports navigation"""
        self.content_panel.clear()
        self.content_panel.add_component(B2bReports())
        self._update_nav_highlights('b2b')

    def _update_nav_highlights(self, active_nav):
        """Helper to update navigation highlighting"""
        self.phone_nav.foreground = app.theme_colors['Secondary'] if active_nav == 'phone' else 'On Secondary Container'
        self.email_nav.foreground = app.theme_colors['Secondary'] if active_nav == 'email' else 'On Secondary Container'
        self.b2b_nav.foreground = app.theme_colors['Secondary'] if active_nav == 'b2b' else 'On Secondary Container'
