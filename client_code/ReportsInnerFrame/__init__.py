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

    def supermove_nav_click(self, **event_args):
        self._switch_section('email', EmailReports())

    def b2b_nav_click(self, **event_args):
        self._switch_section('b2b', B2bReports())
