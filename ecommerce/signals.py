
from django.dispatch import Signal, receiver
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from allauth.account.signals import user_signed_up

from .models import Product, Category
from .utils.emailing import (
    send_welcome_email,
    send_order_confirmation_email,
)


user_registered = Signal()
order_submitted = Signal()


@receiver(user_signed_up, dispatch_uid="ecommerce_welcome_allauth_v1")
def send_welcome_allauth(sender, request, user, **kwargs):
    """Welcome email for allauth signups."""
    try:
        base_url = request.build_absolute_uri('/').rstrip('/') if request else 'https://www.marbaras.com'
        
        # Send email in background, don't fail registration if email fails
        def send_email_safely():
            try:
                send_welcome_email(user, base_url)
            except Exception as e:
                import logging
                log = logging.getLogger(__name__)
                log.exception("Failed to send welcome email to %s: %s", getattr(user, 'email', 'unknown'), e)
        
        transaction.on_commit(send_email_safely)
    except Exception as e:
        import logging
        log = logging.getLogger(__name__)
        log.exception("Error setting up welcome email for user %s: %s", getattr(user, 'email', 'unknown'), e)


@receiver(user_registered, dispatch_uid="ecommerce_welcome_custom_v1")
def send_welcome_custom(sender, user, request=None, **kwargs):
    """Welcome email for your custom register_view."""
    # Skip email sending if email settings are not configured to prevent blocking
    import os
    email_host = os.environ.get('EMAIL_HOST', '')
    if not email_host or email_host == 'sandbox.smtp.mailtrap.io':
        # Email not configured, skip silently
        return
    
    try:
        if request:
            try:
                base_url = request.build_absolute_uri('/').rstrip('/')
            except Exception:
                base_url = 'https://www.marbaras.com'
        else:
            from django.conf import settings
            base_url = getattr(settings, 'SITE_URL', 'https://www.marbaras.com')
        
        # Send email in background with timeout protection
        def send_email_safely():
            try:
                import signal
                # Set a timeout for email sending (5 seconds max)
                def timeout_handler(signum, frame):
                    raise TimeoutError("Email sending timed out")
                
                # Only set timeout if signal module is available (Unix systems)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(5)  # 5 second timeout
                except (AttributeError, OSError):
                    # Windows or signal not available, skip timeout
                    pass
                
                try:
                    send_welcome_email(user, base_url)
                finally:
                    try:
                        signal.alarm(0)  # Cancel timeout
                    except (AttributeError, OSError):
                        pass
            except (TimeoutError, Exception) as e:
                import logging
                log = logging.getLogger(__name__)
                log.exception("Failed to send welcome email to %s: %s", getattr(user, 'email', 'unknown'), e)
        
        transaction.on_commit(send_email_safely)
    except Exception as e:
        import logging
        log = logging.getLogger(__name__)
        log.exception("Error setting up welcome email for user %s: %s", getattr(user, 'email', 'unknown'), e)


@receiver(order_submitted, dispatch_uid="ecommerce_order_confirmation_v1")
def send_order_confirmation(sender, order, request=None, base_url=None, **kwargs):
    """Order confirmation once Order + items are fully saved."""
    if not base_url and request is not None:
        base_url = request.build_absolute_uri('/').rstrip('/')
    transaction.on_commit(lambda: send_order_confirmation_email(order, base_url, notify_admin=True))


# Cache invalidation signals
@receiver(post_save, sender=Category, dispatch_uid="invalidate_categories_cache")
@receiver(post_delete, sender=Category, dispatch_uid="invalidate_categories_cache_delete")
def invalidate_categories_cache(sender, instance, **kwargs):
    """Invalidate categories cache when a category is saved or deleted."""
    cache.delete('all_categories')


@receiver(post_save, sender=Product, dispatch_uid="invalidate_products_cache")
@receiver(post_delete, sender=Product, dispatch_uid="invalidate_products_cache_delete")
def invalidate_products_cache(sender, instance, **kwargs):
    """Invalidate popular products and editors choice cache when a product is saved or deleted."""
    cache.delete('popular_products')
    cache.delete('editors_choice_products')
