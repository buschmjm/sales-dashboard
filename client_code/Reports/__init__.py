from ._anvil_designer import ReportsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import datetime

class Reports(ReportsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Add date selectors
    self.date_selector_1 = DatePicker()
    self.date_selector_2 = DatePicker()
    self.date_selector_3 = DatePicker()
    self.add_component(self.date_selector_1)
    self.add_component(self.date_selector_2)
    self.add_component(self.date_selector_3)

    # Set default dates
    self.date_selector_1.selected_value = datetime.date.today()
    self.date_selector_2.selected_value = datetime.date.today()
    self.date_selector_3.selected_value = datetime.date.today()

    # Line graph for last 7 days of statistics per sales rep
    self.plot_1.data = []
    self.update_line_graph()

    # Pie graph for total volume split by person
    self.plot_2.data = []
    self.update_pie_chart()

    # Data table for selected date range
    self.data_grid.items = []
    self.update_data_table()

    # Date selector event handlers
    self.date_selector_1.change = self.update_line_graph
    self.date_selector_2.change = self.update_pie_chart
    self.date_selector_3.change = self.update_data_table
