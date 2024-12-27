class ThemeColors:
    @staticmethod
    def get_colors(is_dark=False):
        if is_dark:
            return {
                'Primary Container': '#0A84FF',
                'Background': '#000000',
                'Surface': '#1C1C1E',
                'Text': '#FFFFFF',
                'Secondary Text': '#EBEBF5'
            }
        return {
            'Primary Container': '#007AFF',
            'Background': '#FFFFFF',
            'Surface': '#F5F5F5',
            'Text': '#000000',
            'Secondary Text': '#666666'
        }

theme = ThemeColors()
