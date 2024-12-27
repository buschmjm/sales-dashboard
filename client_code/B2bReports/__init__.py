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
    
    # Initialize cache
    self._cache = {}
    
    # Set up color scheme
    self.promo_colors = {
        'Email': '#1f77b4',
        'Flyers': '#ff7f0e',
        'Business Cards': '#2ca02c'
    }
    
    # Initial data refresh
    self.refresh_b2b_data()

  def is_cache_valid(self, start_date, end_date):
    """Check if cached data is still valid"""
    if not self._cache.get('data') or not self._cache.get('last_fetch'):
        return False
    
    cache_age = datetime.now() - self._cache['last_fetch']
    if cache_age.seconds > 300:  # Cache expires after 5 minutes
        return False
        
    return (self._cache['date_range'] == (start_date, end_date))

  def fetch_b2b_data(self, start_date, end_date):
    """Fetch B2B data and update cache"""
    if self.is_cache_valid(start_date, end_date):
        print("Using cached data")
        return self._cache['data']
        
    print("Fetching fresh data")
    all_data = {}
    metrics = ['Email', 'Flyers', 'Business Cards']
    
    for metric in metrics:
        data = anvil.server.call('get_b2b_stats', start_date, end_date, metric)
        if data and "users" in data and "metrics" in data:
            all_data[metric] = data
            
    # Update cache
    self._cache.update({
        'data': all_data,
        'last_fetch': datetime.now(),
        'date_range': (start_date, end_date)
    })
    
    return all_data

  def refresh_b2b_data(self):
    """Refresh plot with all metrics"""
    try:
      # Always fetch all metrics
      all_data = self.fetch_b2b_data(
          self.b2b_start_date.date, 
          self.b2b_end_date.date
      )
      
      if not all_data:
        self._show_empty_plot()
        return
      
      # Get unique sales reps across all metrics
      all_reps = set()
      for data in all_data.values():
        if data["users"] != ["No Data"]:
          all_reps.update(data["users"])
      
      if not all_reps:
        self._show_empty_plot()
        return
      
      sales_reps = sorted(all_reps)
      self._update_stacked_plot(sales_reps, all_data)
      
    except Exception as e:
      alert("Failed to refresh B2B data")
      print(f"Error: {e}")

  def _update_stacked_plot(self, sales_reps, data):
    """Update the stacked bar plot"""
    plot_data = []
    
    for metric in ['Email', 'Flyers', 'Business Cards']:
        if metric in data:
            metrics = data[metric].get("metrics", {})
            values = [metrics.get(rep, 0) for rep in sales_reps]
            
            plot_data.append({
                "type": "bar",
                "name": metric,
                "x": sales_reps,
                "y": values,
                "marker": {"color": self.promo_colors[metric]}
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
    
  def b2b_start_date_change(self, **event_args):
    """Handle start date changes"""
    self._cache = {}  # Invalidate cache when date changes
    self.refresh_b2b_data()

  def b2b_end_date_change(self, **event_args):
    """Handle end date changes"""
    self._cache = {}  # Invalidate cache when date changes
    self.refresh_b2b_data()
