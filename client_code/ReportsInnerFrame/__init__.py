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
        
        # Simplify navigation panel setup
        self.nav_panel.background = 'white'
        self.nav_panel.border = '0 0 1px 0 solid #eee'
        
        # Configure content panel
        self.content_panel.padding = ('12px', 0, 0, 0)
        
        # Initialize navigation buttons with simpler styling
        nav_buttons = [self.phone_nav, self.email_nav, self.b2b_nav]
        for nav in nav_buttons:
            nav.background = "transparent"
            nav.foreground = "black"
            
        # Add initial component after button setup
        self._update_nav_highlights('phone')  # This will set the correct button state
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
        """Simplified navigation highlight update"""
        nav_map = {
            'phone': self.phone_nav,
            'email': self.email_nav,
            'b2b': self.b2b_nav
        }
        
        # Reset all buttons
        for button in nav_map.values():
            button.background = "transparent"
            button.foreground = "black"
        
        # Set active button
        if active_nav in nav_map:
            nav_map[active_nav].background = app.theme_colors['Primary Container']
            nav_map[active_nav].foreground = "white"
