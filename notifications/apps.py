from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    
    def ready(self):
        # import signal handlers
        try:
            import notifications.signals  # noqa: F401
        except Exception:
            pass
