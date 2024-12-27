class Theme:
    _instance = None
    _is_dark = False
    
    def __init__(self):
        self._light_theme = {
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
        
        self._dark_theme = {
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
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_colors(cls):
        instance = cls.get_instance()
        return instance._dark_theme if cls._is_dark else instance._light_theme
    
    @classmethod
    def set_dark_mode(cls, is_dark):
        cls._is_dark = is_dark

theme = Theme.get_instance()
