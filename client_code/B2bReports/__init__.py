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
    
    # Replace metric selector with checkboxes for each promo type
    self.promo_types = ['Email', 'Flyers', 'Business Cards']
    self.selected_promos = set(self.promo_types)  # All selected by default
    
    # Set up color scheme for each promo type
    self.promo_colors = {
        'Email': '#1f77b4',
        'Flyers': '#ff7f0e',
        'Business Cards': '#2ca02c'
    }
    
    # Initial data refresh
    self.refresh_b2b_data()

  def checkbox_change(self, **event_args):
    """Handle checkbox state changes"""
    checkbox = event_args['sender']
    promo_type = checkbox.tag
    
    if checkbox.checked:
        self.selected_promos.add(promo_type)
    else:
        self.selected_promos.remove(promo_type)
    
    self.refresh_b2b_data()

  def b2b_start_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.refresh_b2b_data()

  def b2b_end_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.refresh_b2b_data()
    
  def refresh_b2b_data(self):
    """Fetch and display B2B data for selected promo types"""
    try:
      if not self.selected_promos:
        self._show_empty_plot(error="Please select at least one promotional type")
        return
        
      start_date = self.b2b_start_date.date
      end_date = self.b2b_end_date.date
      
      all_data = {}
      for promo_type in self.selected_promos:
        data = anvil.server.call('get_b2b_stats', start_date, end_date, promo_type)
        if data and "users" in data and "metrics" in data:
          all_data[promo_type] = data
      
      if not all_data:
        self._show_empty_plot()
        return
        
      # Get unique sales reps across all data
      sales_reps = sorted(set().union(*[set(data["users"]) for data in all_data.values()]))
      if "No Data" in sales_reps:
        sales_reps.remove("No Data")
      
      if not sales_reps:
        self._show_empty_plot()
        return
        
      self._update_stacked_plot(sales_reps, all_data)
      
    except Exception as e:
      alert("Failed to refresh B2B data")
      print(f"Error: {e}")
      
  def _update_stacked_plot(self, sales_reps, all_data):
    """Update the plot with stacked bar chart"""
    plot_data = []
    
    for promo_type in self.selected_promos:
      metrics = all_data.get(promo_type, {}).get("metrics", {})
      values = [metrics.get(rep, 0) for rep in sales_reps]
      
      plot_data.append({
        "type": "bar",
        "name": promo_type,
        "x": sales_reps,
        "y": values,
        "marker": {"color": self.promo_colors[promo_type]}
      })
    
    self.b2b_plot.data = plot_data
    self.b2b_plot.layout = {
      "title": f"B2B Marketing Stats ({self.b2b_start_date.date} - {self.b2b_end_date.date})",
      "xaxis": {"title": "Sales Representatives"},
      "yaxis": {"title": "Number of Sales"},
      "showlegend": True,
      "barmode": 'stack'
    }
    
  def _show_empty_plot(self, error=None):
    """Display empty plot with optional error message"""
    message = error if error else "No B2B Statistics Available"
    self.b2b_plot.data = [{"type": "bar", "x": ["No Data"], "y": [0]}]
    self.b2b_plot.layout.update({
      "title": message,
      "xaxis": {"title": "Sales Representatives"},
      "yaxis": {"title": "Number of Sales"},
      "showlegend": False
    })
