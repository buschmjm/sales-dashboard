@anvil.server.callable
def save_user_theme_preference(theme):
    """Save user's theme preference"""
    user = anvil.users.get_user()
    if user:
        user['theme_preference'] = theme
        user.update()
