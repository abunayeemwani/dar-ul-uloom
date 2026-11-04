from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Darul Uloom Sabeel Ul Rasool Administration'

    def ready(self):
        import core.signals