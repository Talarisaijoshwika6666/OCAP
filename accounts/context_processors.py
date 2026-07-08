def theme(request):
    """Makes the logged-in user's saved Appearance theme ('dark'/'light')
    available in every template as {{ active_theme }}, so base.html can set
    it on <html data-theme="..."> before first paint (no flash)."""
    active_theme = 'dark'
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        settings_obj = getattr(user, 'settings', None)
        if settings_obj is not None:
            active_theme = settings_obj.theme
    return {'active_theme': active_theme}
