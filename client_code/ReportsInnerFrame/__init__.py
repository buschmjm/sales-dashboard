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
        # Set fixed dimensions
        properties['height'] = '900'
        properties['width'] = '100%'
        self.init_components(**properties)
        
        # Set content panel dimensions
        self.content_panel.height = '800'
        self.content_panel.width = '100%'
        self.content_panel.role = 'none'
        
        # Basic initialization
        self.current_section = 'phone'
        
        # Configure navigation with fixed dimensions
        for nav in [self.phone_nav, self.email_nav, self.b2b_nav]:
            nav.background = 'transparent'
            nav.foreground = 'black'
            nav.role = 'none'
            nav.width = '100'
            nav.height = '40'
        
        # Initialize with phone view
        self.content_panel.add_component(PhoneReports())
        self.phone_nav.background = app.theme_colors['Primary Container']
        self.phone_nav.foreground = 'white'

    def _switch_section(self, section, component):
        """Handle section switching"""
        if self.current_section != section:
            self.current_section = section
            self.content_panel.clear()
            
            # Set fixed dimensions for new component
            component.width = '100%'
            component.height = '800'
            self.content_panel.add_component(component)
            
            # Reset all nav buttons
            for nav in [self.phone_nav, self.email_nav, self.b2b_nav]:
                nav.background = 'transparent'
                nav.foreground = 'black'
            
            # Set active button
            active_nav = getattr(self, f"{section}_nav")
            active_nav.background = app.theme_colors['Primary Container']
            active_nav.foreground = 'white'

    def phone_nav_click(self, **event_args):
        self._switch_section('phone', PhoneReports())

    def email_nav_click(self, **event_args):
        self._switch_section('email', EmailReports())

    def b2b_nav_click(self, **event_args):
        self._switch_section('b2b', B2bReports())
