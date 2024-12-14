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
        
        # Set the role to 'none' for the content panel like in Frame
        self.content_panel.role = 'none'
        
        # Simple navigation setup without custom styling
        nav_buttons = [self.phone_nav, self.email_nav, self.b2b_nav]
        for nav in nav_buttons:
            nav.background = "transparent"
            nav.foreground = "black"
            nav.role = 'primary-color'  # Use Anvil's built-in roles
        
        # Load initial view
        self._update_nav_highlights('phone')
        self.content_panel.add_component(PhoneReports())

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
        """Simplified navigation highlight update using Anvil properties"""
        nav_map = {
            'phone': self.phone_nav,
            'email': self.email_nav,
            'b2b': self.b2b_nav
        }
        
        # Reset all buttons
        for button in nav_map.values():
            button.role = 'primary-color'
            button.background = "transparent"
            button.foreground = "black"
        
        # Set active button
        if active_nav in nav_map:
            nav_map[active_nav].background = app.theme_colors['Primary Container']
            nav_map[active_nav].foreground = "white"
