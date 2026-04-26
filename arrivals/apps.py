from django.apps import AppConfig

class ArrivalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'arrivals'
    verbose_name = 'Confirm New Arrivals'

    def ready(self):
        import arrivals.signals  # noqa: F401
