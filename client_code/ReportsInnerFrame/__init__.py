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
        self._update_nav_highlights('phone')
        
        # Add hover effects to navigation buttons
        for nav in [self.phone_nav, self.email_nav, self.b2b_nav]:
            nav.background = "transparent"
            nav.hover_background = self._get_hover_color()

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

    def _get_hover_color(self):
        """Returns a slightly lighter version of Primary Container for hover effects"""
        return app.theme_colors['Surface Variant']

    def _update_nav_highlights(self, active_nav):
        """Helper to update navigation highlighting"""
        # Reset all backgrounds first
        self.phone_nav.background = "transparent"
        self.email_nav.background = "transparent"
        self.b2b_nav.background = "transparent"
        
        # Set active background
        if active_nav == 'phone':
            self.phone_nav.background = app.theme_colors['Primary Container']
        elif active_nav == 'email':
            self.email_nav.background = app.theme_colors['Primary Container']
        elif active_nav == 'b2b':
            self.b2b_nav.background = app.theme_colors['Primary Container']
