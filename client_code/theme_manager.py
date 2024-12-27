class ThemeManager:
    _instance = None
    _current_theme = None
    
    @classmethod
    def initialize(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._current_theme = cls._instance.get_light_theme()
    
    @staticmethod
    def get_light_theme():
        return {
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
            'Plot': {
                'Background': '#FFFFFF',
                'Text': '#191C1A',
                'Grid': '#E1E3DF'
            }
        }
    
    @staticmethod
    def get_dark_theme():
        return {
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
            'Plot': {
                'Background': '#191C1A',
                'Text': '#E1E3DF',
                'Grid': '#404943'
            }
        }
    
    @classmethod
    def get_theme(cls):
        if cls._current_theme is None:
            cls.initialize()
        return cls._current_theme
    
    @classmethod
    def set_theme(cls, is_dark):
        cls._current_theme = cls.get_dark_theme() if is_dark else cls.get_light_theme()

# Initialize theme manager
ThemeManager.initialize()
