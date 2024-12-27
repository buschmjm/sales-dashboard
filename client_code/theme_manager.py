class ThemeManager:
    _instance = None
    _current_theme = None
    
    def __init__(self):
        self.light_theme = {
            'Button': {
                'Default': '#1EB980',
                'Active': '#005235',
                'Hover': '#73FBBC',
                'Text': '#FFFFFF',
                'Text Active': '#73FBBC',
                'Text Inactive': '#000000'
            },
            'Primary': '#1EB980',
            'Primary Container': '#005235',
            'Background': '#FFFFFF',
            'Surface': '#F5F5F5',
            'Surface Variant': '#E1E3DF',
            'Text': '#191C1A',
            'Secondary Text': '#404943',
            'Plot': {
                'Background': '#FFFFFF',
                'Text': '#191C1A',
                'Grid': '#E1E3DF'
            }
        }
        
        self.dark_theme = {
            'Button': {
                'Default': '#1EB980',
                'Active': '#005235',
                'Hover': '#73FBBC',
                'Text': '#FFFFFF',
                'Text Active': '#73FBBC',
                'Text Inactive': '#E1E3DF'
            },
            'Primary': '#1EB980',
            'Primary Container': '#005235',
            'Background': '#191C1A',
            'Surface': '#191C1A',
            'Surface Variant': '#404943',
            'Text': '#E1E3DF',
            'Secondary Text': '#C0C9C1',
            'Plot': {
                'Background': '#191C1A',
                'Text': '#E1E3DF',
                'Grid': '#404943'
            }
        }
        ThemeManager._current_theme = dict(self.light_theme)
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = ThemeManager()
        return cls._instance
    
    @classmethod
    def get_theme(cls):
        return cls.get_instance()._current_theme
    
    @classmethod
    def set_theme(cls, is_dark):
        instance = cls.get_instance()
        new_theme = instance.dark_theme if is_dark else instance.light_theme
        cls._current_theme.clear()
        cls._current_theme.update(new_theme)
