class ThemeColors:
    @staticmethod
    def get_colors(is_dark=False):
        if is_dark:
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
                'Secondary Text': '#C0C9C1',
                'Plot': {
                    'Background': '#191C1A',
                    'Text': '#E1E3DF',
                    'Grid': '#404943'
                }
            }
        # Light theme colors
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
            'Secondary Text': '#404943',
            'Plot': {
                'Background': '#FFFFFF',
                'Text': '#191C1A',
                'Grid': '#E1E3DF'
            }
        }

theme = ThemeColors()
