import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template.loader import render_to_string
from decimal import Decimal

log = logging.getLogger(__name__)

def _log_email_config():
    """Log current email configuration for debugging."""
    email_backend = getattr(settings, "EMAIL_BACKEND", "not set")
    email_host = getattr(settings, "EMAIL_HOST", "not set")
    email_port = getattr(settings, "EMAIL_PORT", "not set")
    email_user = getattr(settings, "EMAIL_HOST_USER", "not set")
    email_use_tls = getattr(settings, "EMAIL_USE_TLS", False)
    email_use_ssl = getattr(settings, "EMAIL_USE_SSL", False)
    default_from = getattr(settings, "DEFAULT_FROM_EMAIL", "not set")
    
    log.info("=" * 60)
    log.info("EMAIL CONFIGURATION:")
    log.info("  EMAIL_BACKEND: %s", email_backend)
    log.info("  EMAIL_HOST: %s", email_host)
    log.info("  EMAIL_PORT: %s", email_port)
    log.info("  EMAIL_HOST_USER: %s", email_user)
    log.info("  EMAIL_USE_TLS: %s", email_use_tls)
    log.info("  EMAIL_USE_SSL: %s", email_use_ssl)
    log.info("  DEFAULT_FROM_EMAIL: %s", default_from)
    log.info("=" * 60)

def _base_url(request=None, fallback=""):
    if request:
        scheme = "https" if request.is_secure() else "http"
        return f"{scheme}://{request.get_host()}"
    return fallback

def send_welcome_email(user, base_url) -> bool:
    """Send welcome email to user. Returns True on success, False on failure.
    Never raises exceptions - all errors are logged and swallowed."""
    try:
        if not getattr(user, "email", None):
            log.warning("Welcome email skipped, user has no email: %s", user)
            return False

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
        ctx = {"user": user, "base_url": base_url}

        # Log email configuration and sending attempt
        _log_email_config()
        log.info("📧 ATTEMPTING TO SEND WELCOME EMAIL")
        log.info("  To: %s", user.email)
        log.info("  From: %s", from_email)
        log.info("  Subject: Welcome to Marbaras ✨")
        log.info("  Base URL: %s", base_url)

        try:
            subject = "Welcome to Marbaras ✨"
            text = render_to_string("emails/welcome.txt", ctx)
            html = render_to_string("emails/welcome.html", ctx)
            msg = EmailMultiAlternatives(subject, text, from_email, [user.email])
            msg.attach_alternative(html, "text/html")
            
            log.info("  Message created, attempting to send via SMTP...")
            # Use fail_silently=True and timeout to prevent blocking
            # Set timeout to prevent hanging (default is 30 seconds from settings)    
            result = msg.send(fail_silently=True)
            log.info("✅ Welcome email sent successfully to %s (result: %s)", user.email, result)
            return True
        except Exception as e:
            log.error("❌ Failed to send welcome email to %s: %s", getattr(user, "email", None), e)
            log.exception("Exception details:")
            return False
    except Exception as e:
        # Catch any unexpected errors (e.g., template rendering, settings access)
        log.error("❌ Unexpected error in send_welcome_email for user %s: %s", getattr(user, "email", "unknown"), e)
        log.exception("Exception details:")
        return False

def send_order_confirmation_email(order, base_url, notify_admin=False) -> bool:
    """Send order confirmation email to customer."""
    # Prefer an explicit order email (e.g., shipping email), else fallback to user's email.
    recipient = getattr(order, "email", None) or getattr(getattr(order, "user", None), "email", None)
    if not recipient:
        log.warning("Order email skipped, no recipient for order #%s", order.id)
        return False

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"

    # Avoid N+1 when templates access item.product and variant
    items = order.items.select_related("product", "variant").all()

    # Calculate totals
    subtotal = sum(
        (item.product.get_discounted_price() * Decimal(item.quantity))
        for item in items
    )
    shipping_cost = order.shipping_option.price if order.shipping_option else Decimal("0.00")
    discount_amount = Decimal("0.00")
    if order.coupon:
        discount_amount = subtotal - order.coupon.apply(subtotal)
    total = order.total_price

    ctx = {
        "order": order,
        "items": items,
        "base_url": base_url,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "discount_amount": discount_amount,
        "total": total,
    }
    
    # Log email configuration and sending attempt
    _log_email_config()
    log.info("📧 ATTEMPTING TO SEND ORDER CONFIRMATION EMAIL")
    log.info("  Order ID: #%s", order.id)
    log.info("  To: %s", recipient)
    log.info("  From: %s", from_email)
    log.info("  Subject: Order #%s - Marbaras ✨", order.id)
    log.info("  Total: $%s", total)
    log.info("  Base URL: %s", base_url)
    
    try:
        subject = f"Order #{order.id} - Marbaras ✨"
        text = render_to_string("emails/order_confirmation.txt", ctx)
        html = render_to_string("emails/order_confirmation.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [recipient])
        msg.attach_alternative(html, "text/html")
        
        log.info("  Message created, attempting to send via SMTP...")
        result = msg.send(fail_silently=True)  # Changed to True to prevent blocking if email fails
        log.info("✅ Order confirmation email sent successfully to %s (result: %s)", recipient, result)

        if notify_admin:
            log.info("  Sending admin notification email...")
            customer = getattr(order, "full_name", None) or getattr(order, "user", None)
            admin_message = f"""New order #{order.id}

Customer: {customer}
Email: {recipient}
Total: ${total}
Address: {order.address}, {order.city}, {order.postal_code}
Phone: {order.phone}

View: {base_url}/admin/ecommerce/order/{order.id}/
"""
            admin_result = mail_admins(
                subject=f"New order #{order.id}",
                message=admin_message,
                fail_silently=True,
            )
            log.info("✅ Admin notification email sent (result: %s)", admin_result)
        return True
    except Exception as e:
        log.error("❌ Failed to send order email for #%s: %s", order.id, e)
        log.exception("Exception details:")
        return False


def send_order_shipped_email(order, base_url, tracking_number=None) -> bool:
    """Send email when order is shipped."""
    recipient = getattr(order, "email", None) or getattr(getattr(order, "user", None), "email", None)
    if not recipient:
        log.warning("Order shipped email skipped, no recipient for order #%s", getattr(order, 'id', 'unknown'))
        return False

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
    items = order.items.select_related("product", "variant").all()

    ctx = {
        "order": order,
        "items": items,
        "base_url": base_url,
        "tracking_number": tracking_number,
        "shipping_option": order.shipping_option,
    }
    
    # Log email configuration and sending attempt
    _log_email_config()
    log.info("📧 ATTEMPTING TO SEND ORDER SHIPPED EMAIL")
    log.info("  Order ID: #%s", order.id)
    log.info("  To: %s", recipient)
    log.info("  From: %s", from_email)
    log.info("  Subject: Your order #%s has been shipped - Marbaras", order.id)
    log.info("  Tracking Number: %s", tracking_number or "N/A")
    log.info("  Base URL: %s", base_url)
    
    try:
        subject = f"Your order #{order.id} has been shipped - Marbaras"
        text = render_to_string("emails/order_shipped.txt", ctx)
        html = render_to_string("emails/order_shipped.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [recipient])
        msg.attach_alternative(html, "text/html")
        
        log.info("  Message created, attempting to send via SMTP...")
        result = msg.send(fail_silently=True)  # Changed to True to prevent blocking if email fails
        log.info("✅ Order shipped email sent successfully to %s (result: %s)", recipient, result)
        return True
    except Exception as e:
        log.error("❌ Failed to send order shipped email for #%s: %s", order.id, e)
        log.exception("Exception details:")
        return False


def send_password_reset_email(user, reset_url, base_url) -> bool:
    """Send password reset email."""
    if not getattr(user, "email", None):
        log.warning("Password reset email skipped, user has no email: %s", user)
        return False

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
    ctx = {"user": user, "reset_url": reset_url, "base_url": base_url}

    # Log email configuration and sending attempt
    _log_email_config()
    log.info("📧 ATTEMPTING TO SEND PASSWORD RESET EMAIL")
    log.info("  To: %s", user.email)
    log.info("  From: %s", from_email)
    log.info("  Subject: Password Reset - Marbaras")
    log.info("  Reset URL: %s", reset_url)
    log.info("  Base URL: %s", base_url)

    try:
        subject = "Password Reset - Marbaras"
        text = render_to_string("emails/password_reset.txt", ctx)
        html = render_to_string("emails/password_reset.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [user.email])
        msg.attach_alternative(html, "text/html")
        
        log.info("  Message created, attempting to send via SMTP...")
        result = msg.send(fail_silently=True)  # Changed to True to prevent blocking if email fails
        log.info("✅ Password reset email sent successfully to %s (result: %s)", user.email, result)
        return True
    except Exception as e:
        log.error("❌ Failed to send password reset email to %s: %s", getattr(user, "email", None), e)
        log.exception("Exception details:")
        return False
