
from django.apps import AppConfig

class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self):
        from . import signals
        
        # Import template tags to ensure they are registered
        try:
            import ecommerce.template_tags.blog_filters  # noqa
            import ecommerce.template_tags.cart_extras  # noqa
        except ImportError:
            pass
