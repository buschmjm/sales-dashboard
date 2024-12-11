from ._anvil_designer import SalesTemplate
from anvil import *
import .. 

class Sales(SalesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Add a frame overlay for the page
    self.frame = Frame()
    self.add_component(self.frame, slot='frame')