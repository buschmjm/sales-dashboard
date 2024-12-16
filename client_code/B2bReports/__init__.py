from ._anvil_designer import B2bReportsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, date

class B2bReports(B2bReportsTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    # Set default date range
    self.b2b_end_date.date = date.today()
    self.b2b_start_date.date = date.today() - timedelta(days=7)
    
    # Set up metrics dropdown
    self.metric_display_names = {
        'Email': 'Email Marketing',
        'Flyers': 'Flyer Marketing',
        'Business Cards': 'Business Card Marketing'
    }
    
    self.b2b_metric_selector.items = [
        (name, key) for key, name in self.metric_display_names.items()
    ]
    self.b2b_metric_selector.selected_value = 'Email'
    
    # Initial data refresh
    self.refresh_b2b_data()

  def b2b_metric_selector_change(self, **event_args):
    """This method is called when an item is selected"""
    self.refresh_b2b_data()

  def b2b_start_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.refresh_b2b_data()

  def b2b_end_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.refresh_b2b_data()
    
  def refresh_b2b_data(self):
    """Fetch and display B2B data based on current selections"""
    try:
      start_date = self.b2b_start_date.date
      end_date = self.b2b_end_date.date
      metric = self.b2b_metric_selector.selected_value
      
      # Get data from server
      data = anvil.server.call('get_b2b_stats', start_date, end_date, metric)
      
      if not data or "users" not in data or "metrics" not in data:
        self._show_empty_plot()
        return
        
      sales_reps = data["users"]
      if sales_reps == ["No Data"]:
        self._show_empty_plot()
        return
        
      metric_values = [data["metrics"].get(rep, 0) for rep in sales_reps]
      self._update_b2b_plot(sales_reps, metric_values)
      
    except Exception as e:
      alert("Failed to refresh B2B data")
      print(f"Error: {e}")
      
  def _update_b2b_plot(self, sales_reps, metric_values):
    """Update the B2B plot with new data"""
    if not sales_reps:
      self._show_empty_plot()
      return
      
    metric_display_name = self.metric_display_names[self.b2b_metric_selector.selected_value]
    
    plot_data = {
      "type": "bar",
      "x": sales_reps,
      "y": metric_values,
      "name": metric_display_name
    }
    
    self.b2b_plot.data = [plot_data]
    self.b2b_plot.layout = {
      "title": f"{metric_display_name} ({self.b2b_start_date.date} - {self.b2b_end_date.date})",
      "xaxis": {"title": "Sales Representatives"},
      "yaxis": {"title": "Number of Sales"},
      "showlegend": True,
      "barmode": 'group'
    }
    
  def _show_empty_plot(self, error=None):
    """Display empty plot when no data is available"""
    message = "No B2B Statistics Available" if not error else f"Error: {error}"
    self.b2b_plot.data = [{"type": "bar", "x": ["No Data"], "y": [0]}]
    self.b2b_plot.layout.update({
      "title": message,
      "xaxis": {"title": "Sales Representatives"},
      "yaxis": {"title": "Number of Sales"},
      "showlegend": False,
    })
