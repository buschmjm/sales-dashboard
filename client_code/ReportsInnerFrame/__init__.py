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
        
        # Configure content panel
        self.content_panel.spacing_above = 'none'
        self.content_panel.spacing_below = 'none'
        self.content_panel.role = 'none'
        
        # Basic initialization
        self.current_section = 'phone'
        
        # Configure navigation
        for nav in [self.phone_nav, self.email_nav, self.b2b_nav]:
            nav.background = 'transparent'
            nav.foreground = 'black'
            nav.role = 'none'
            nav.spacing_above = 'none'
            nav.spacing_below = 'none'
        
        # Initialize with phone view
        component = PhoneReports()
        component.spacing_above = 'none'
        component.spacing_below = 'none'
        self.content_panel.add_component(component)
        self.phone_nav.background = app.theme_colors['Primary Container']
        self.phone_nav.foreground = 'white'

    def _switch_section(self, section, component):
        if self.current_section != section:
            self.current_section = section
            self.content_panel.clear()
            
            # Configure component
            component.spacing_above = 'none'
            component.spacing_below = 'none'
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
