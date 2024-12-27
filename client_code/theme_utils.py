class ThemeColors:
    @staticmethod
    def get_colors(is_dark=False):
        if is_dark:
            return {
                # Primary colors
                'Primary': '#1EB980',
                'Primary Container': '#005235',
                'On Primary': '#003824',
                'On Primary Container': '#73FBBC',
                
                # Secondary colors
                'Secondary': '#B4CCBC',
                'Secondary Container': '#364B3F',
                'On Secondary': '#20352A',
                'On Secondary Container': '#D0E8D8',
                
                # Tertiary colors
                'Tertiary': '#A4CDDD',
                'Tertiary Container': '#234C5A',
                'On Tertiary': '#063542',
                'On Tertiary Container': '#C0E9FA',
                
                # Background and surface colors
                'Background': '#191C1A',
                'Surface': '#191C1A',
                'Surface Variant': '#404943',
                'On Background': '#E1E3DF',
                'On Surface': '#E1E3DF',
                'On Surface Variant': '#C0C9C1',
                
                # Utility colors
                'Error': '#D64D47',
                'Outline': '#8A938C',
                'Text': '#E1E3DF',  # Using On Surface for text
                
                # Overlay colors
                'Dark Overlay 1': 'rgba(208, 232, 216, 0.2)',
                'Dark Overlay 2': 'rgba(208, 232, 216, 0.5)',
                'Light Overlay 1': 'rgba(208, 232, 216, 0.2)',
                'Light Overlay 2': 'rgba(208, 232, 216, 0.5)',
                'Primary Overlay 1': 'rgba(30, 185, 128, 0.05)',
                'Primary Overlay 2': 'rgba(30, 185, 128, 0.08)',
                'Primary Overlay 3': 'rgba(30, 185, 128, 0.11)',
                
                # Disabled states
                'Disabled Container': 'rgba(133, 133, 139, 0.12)',
                'On Disabled': '#85858B'
            }
        return {
            'Primary Container': '#007AFF',
            'Background': '#FFFFFF',
            'Surface': '#F5F5F5',
            'Text': '#000000',
            'Secondary Text': '#666666'
        }

theme = ThemeColors()
