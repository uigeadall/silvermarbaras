
from django.dispatch import Signal, receiver
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from allauth.account.signals import user_signed_up
import logging

log = logging.getLogger(__name__)

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
    log.info("🔔 SIGNAL TRIGGERED: user_signed_up (allauth) for user: %s (email: %s)", 
             getattr(user, 'username', 'unknown'), getattr(user, 'email', 'no email'))
    try:
        base_url = request.build_absolute_uri('/').rstrip('/') if request else 'https://www.marbaras.com'
        log.info("  Base URL determined: %s", base_url)
        
        # Send email in background, don't fail registration if email fails
        def send_email_safely():
            log.info("  Executing send_welcome_email in transaction.on_commit callback...")
            try:
                send_welcome_email(user, base_url)
            except Exception as e:
                log.error("  ❌ Exception in send_email_safely callback: %s", e)
                log.exception("Exception details:")
        
        transaction.on_commit(send_email_safely)
        log.info("  ✅ Welcome email scheduled to be sent after transaction commit")
    except Exception as e:
        log.error("❌ Error setting up welcome email for user %s: %s", getattr(user, 'email', 'unknown'), e)
        log.exception("Exception details:")


@receiver(user_registered, dispatch_uid="ecommerce_welcome_custom_v1")
def send_welcome_custom(sender, user, request=None, **kwargs):
    """Welcome email for your custom register_view."""
    log.info("🔔 SIGNAL TRIGGERED: user_registered (custom) for user: %s (email: %s)", 
             getattr(user, 'username', 'unknown'), getattr(user, 'email', 'no email'))
    
    # Skip email sending if email settings are not configured to prevent blocking
    import os
    email_host = os.environ.get('EMAIL_HOST', '')
    log.info("  EMAIL_HOST environment variable: %s", email_host if email_host else '(not set)')
    
    if not email_host or email_host == 'sandbox.smtp.mailtrap.io':
        # Email not configured, skip silently
        log.info("  ⚠️  Email sending skipped - EMAIL_HOST not configured or is sandbox")
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
        
        # Send email in background
        # Note: Removed signal-based timeout as it interferes with SMTP connection
        # Django's EMAIL_TIMEOUT setting handles timeouts properly
        def send_email_safely():
            log.info("  Executing send_welcome_email in transaction.on_commit callback...")
            try:
                send_welcome_email(user, base_url)
            except Exception as e:
                log.error("  ❌ Exception in send_email_safely callback: %s", e)
                log.exception("Exception details:")
        
        transaction.on_commit(send_email_safely)
        log.info("  ✅ Welcome email scheduled to be sent after transaction commit")
    except Exception as e:
        log.error("❌ Error setting up welcome email for user %s: %s", getattr(user, 'email', 'unknown'), e)
        log.exception("Exception details:")


@receiver(order_submitted, dispatch_uid="ecommerce_order_confirmation_v1")
def send_order_confirmation(sender, order, request=None, base_url=None, **kwargs):
    """Order confirmation once Order + items are fully saved."""
    log.info("🔔 SIGNAL TRIGGERED: order_submitted for order #%s", getattr(order, 'id', 'unknown'))
    
    # Determine base_url
    if not base_url:
        if request is not None:
            try:
                base_url = request.build_absolute_uri('/').rstrip('/')
            except Exception:
                base_url = 'https://www.marbaras.com'
        else:
            base_url = 'https://www.marbaras.com'
    
    log.info("  Base URL determined: %s", base_url)
    log.info("  Order details: ID=%s, Total=$%s", getattr(order, 'id', 'unknown'), getattr(order, 'total_price', 'unknown'))
    
    # Use proper function instead of lambda to avoid closure issues
    def send_email_safely():
        log.info("  Executing send_order_confirmation_email in transaction.on_commit callback...")
        try:
            send_order_confirmation_email(order, base_url, notify_admin=True)
        except Exception as e:
            log.error("  ❌ Exception in send_email_safely callback: %s", e)
            log.exception("Exception details:")
    
    transaction.on_commit(send_email_safely)
    log.info("  ✅ Order confirmation email scheduled to be sent after transaction commit")


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
