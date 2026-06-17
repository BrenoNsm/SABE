from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sabe.apps.core'
    verbose_name = 'Núcleo'

    def ready(self):
        import sabe.apps.core.signals  # noqa
