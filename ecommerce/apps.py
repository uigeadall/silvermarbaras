# ecommerce/apps.py
from django.apps import AppConfig

class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self):
        # Register signal receivers at startup
        from . import signals  # noqa: F401
