class ThemeService:
    def __init__(self):
        self.light_theme = {
            'Primary Container': '#007AFF',
            'Background': '#FFFFFF',
            'Surface': '#F5F5F5',
            'Text': '#000000',
            'Secondary Text': '#666666'
        }
        
        self.dark_theme = {
            'Primary Container': '#0A84FF',
            'Background': '#000000',
            'Surface': '#1C1C1E',
            'Text': '#FFFFFF',
            'Secondary Text': '#EBEBF5'
        }
        
        self.current_theme = dict(self.light_theme)
    
    def get_color(self, key):
        return self.current_theme.get(key)
    
    def set_theme(self, is_dark):
        self.current_theme.clear()
        self.current_theme.update(self.dark_theme if is_dark else self.light_theme)

# Create a singleton instance
theme = ThemeService()
