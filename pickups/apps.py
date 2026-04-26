from django.apps import AppConfig

class PickupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pickups'
    verbose_name = 'Confirm Delivery Pickup'

    def ready(self):
        import pickups.signals  # noqa: F401
