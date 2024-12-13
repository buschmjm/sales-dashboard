from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.http
from anvil.tables import app_tables
from ..Reports import Reports
from ..Sales import Sales
from ..Admin import Admin
from datetime import datetime

class Frame(FrameTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self._ensure_user_authenticated()

    def _ensure_user_authenticated(self):
        """Ensure user is authenticated before accessing the application."""
        try:
            if not anvil.users.get_user():
                anvil.users.login_with_form()
            if not anvil.users.get_user():
                raise Exception("Authentication required")
        except Exception as e:
            alert("Authentication failed. Please try again.")
            raise

    def refresh_button_click(self, **event_args):
        """Handle refresh button click to fetch call reports and email stats."""
        try:
            with anvil.server.no_loading_indicator:
                call_reports_result = anvil.server.call('fetch_call_reports')
                email_stats = anvil.server.call('fetch_user_email_stats')
                
                if call_reports_result and email_stats:
                    alert("Data refreshed successfully!")
                return {
                    "success": True,
                    "email_stats": email_stats,
                    "call_reports_refreshed": call_reports_result
                }
        except Exception as e:
            alert(f"Error refreshing data: {str(e)}")
            return {"error": str(e)}

    def _update_nav_highlights(self, active_link):
        """Update navigation link highlights."""
        nav_links = {
            'sales': self.sales_page_link,
            'reports': self.reports_page_link,
            'admin': self.admin_page_link
        }
        
        for link_name, link in nav_links.items():
            link.background = (
                app.theme_colors['Primary Container'] 
                if link_name == active_link 
                else "transparent"
            )

    def _load_page(self, component_class, page_name):
        """Generic method to load pages with error handling."""
        try:
            self.content_panel.clear()
            self.content_panel.add_component(component_class())
            self._update_nav_highlights(page_name)
        except Exception as e:
            alert(f"Error loading {page_name} page: {str(e)}")
            raise

    def sales_page_link_click(self, **event_args):
        self._load_page(Sales, 'sales')

    def reports_page_link_click(self, **event_args):
        self._load_page(Reports, 'reports')

    def admin_page_link_click(self, **event_args):
        self._load_page(Admin, 'admin')

    def signout_link_click(self, **event_args):
        try:
            anvil.users.logout()
            self._ensure_user_authenticated()
        except Exception as e:
            alert(f"Error during sign out: {str(e)}")


def update_call_statistics(data):
    today_date = datetime.utcnow().date()

    for item in data.get("items", []):
        user_id = item["userId"]
        user_name = item["userName"]
        data_values = item["dataValues"]

        # Check if a record exists for this user ID and today's date
        existing_row = app_tables.call_statistics.get(
            userId=user_id, reportDate=today_date
        )

        if existing_row:
            # Update the existing record
            existing_row.update(
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
            )
        else:
            # Add a new record
            app_tables.call_statistics.add_row(
                userId=user_id,
                userName=user_name,
                inboundVolume=data_values["inboundVolume"],
                inboundDuration=data_values["inboundDuration"],
                outboundVolume=data_values["outboundVolume"],
                outboundDuration=data_values["outboundDuration"],
                averageDuration=data_values["averageDuration"],
                volume=data_values["volume"],
                totalDuration=data_values["totalDuration"],
                inboundQueueVolume=data_values["inboundQueueVolume"],
                reportDate=today_date,
            )

def get_access_token():
    """Retrieve API access token."""
    try:
        # Implement your token retrieval logic here
        token = anvil.server.call('get_api_token')
        if not token:
            raise ValueError("Failed to retrieve access token")
        return token
    except Exception as e:
        print(f"Error getting access token: {e}")
        raise

def fetch_user_stats(email, headers, today):
    try:
        url = f"https://api.example.com/user_stats?email={email}&date={today}"
        response = anvil.http.request(url, method="GET", headers=headers, json=True)
        if response.status_code == 200:
            return response.get_bytes()
        else:
            raise Exception(f"Failed to fetch user stats: {response.status_code} - {response.content}")
    except Exception as e:
        print(f"Error fetching user stats for {email}: {e}")
        raise
