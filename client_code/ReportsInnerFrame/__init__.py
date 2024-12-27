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
from .. import theme_utils


class ReportsInnerFrame(ReportsInnerFrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Add table styling
        if hasattr(self, 'repeating_panel_1'):
            self.repeating_panel_1.role = 'table'
        
        # Basic initialization
        self.content_panel.role = 'none'
        self.current_section = 'phone'
        
        # Configure navigation
        for nav in [self.phone_nav, self.email_nav, self.b2b_nav]:
            nav.background = 'transparent'
            nav.foreground = 'black'
            nav.role = 'none'
        
        # Initialize with phone view
        self.content_panel.add_component(PhoneReports())
        self.phone_nav.background = app.theme_colors['Primary Container']
        self.phone_nav.foreground = 'white'

    def _switch_section(self, section, component):
        if self.current_section != section:
            self.current_section = section
            self.content_panel.clear()
            self.content_panel.add_component(component)
            
            colors = theme_utils.theme.get_colors(self._get_theme_mode())
            button_colors = colors['Button']
            
            # Reset all nav buttons
            for nav in [self.phone_nav, self.email_nav, self.b2b_nav]:
                nav.background = 'transparent'
                nav.foreground = button_colors['Text Inactive']
            
            # Set active button
            active_nav = getattr(self, f"{section}_nav")
            active_nav.background = button_colors['Active']
            active_nav.foreground = button_colors['Text Active']

    def _get_theme_mode(self):
        """Get current theme mode from parent Frame"""
        return getattr(self.parent.parent, 'is_dark_mode', False)

    def phone_nav_click(self, **event_args):
        self._switch_section('phone', PhoneReports())

    def email_nav_click(self, **event_args):
        self._switch_section('email', EmailReports())

    def b2b_nav_click(self, **event_args):
        self._switch_section('b2b', B2bReports())
