
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins, send_mail
from django.template.loader import render_to_string
from decimal import Decimal

log = logging.getLogger(__name__)

def _base_url(request=None, fallback=""):
    if request:
        scheme = "https" if request.is_secure() else "http"
        return f"{scheme}://{request.get_host()}"
    return fallback

def send_welcome_email(user, base_url) -> bool:
    if not getattr(user, "email", None):
        log.warning("Welcome email skipped, user has no email: %s", user)
        return False

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
    ctx = {"user": user, "base_url": base_url}

    try:
        subject = "Welcome to Marbaras ✨"
        text = render_to_string("emails/welcome.txt", ctx)
        html = render_to_string("emails/welcome.html", ctx)
        msg = EmailMultiAlternatives(subject, text, from_email, [user.email])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        log.exception("Failed to send welcome email to %s: %s", getattr(user, "email", None), e)
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
    try:
        subject = f"Order #{order.id} - Marbaras ✨"
        text = render_to_string("emails/order_confirmation.txt", ctx)
        html = render_to_string("emails/order_confirmation.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [recipient])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

        if notify_admin:
            customer = getattr(order, "full_name", None) or getattr(order, "user", None)
            admin_message = f"""New order #{order.id}

Customer: {customer}
Email: {recipient}
Total: ${total}
Address: {order.address}, {order.city}, {order.postal_code}
Phone: {order.phone}

View: {base_url}/admin/ecommerce/order/{order.id}/
"""
            mail_admins(
                subject=f"New order #{order.id}",
                message=admin_message,
                fail_silently=True,
            )
        return True
    except Exception as e:
        log.exception("Failed to send order email for #%s: %s", order.id, e)
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
    try:
        subject = f"Your order #{order.id} has been shipped - Marbaras"
        text = render_to_string("emails/order_shipped.txt", ctx)
        html = render_to_string("emails/order_shipped.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [recipient])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        log.exception("Failed to send order shipped email for #%s: %s", order.id, e)
        return False


def send_password_reset_email(user, reset_url, base_url) -> bool:
    """Send password reset email."""
    if not getattr(user, "email", None):
        log.warning("Password reset email skipped, user has no email: %s", user)
        return False

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"
    ctx = {"user": user, "reset_url": reset_url, "base_url": base_url}

    try:
        subject = "Password Reset - Marbaras"
        text = render_to_string("emails/password_reset.txt", ctx)
        html = render_to_string("emails/password_reset.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [user.email])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        log.exception("Failed to send password reset email to %s: %s", getattr(user, "email", None), e)
        return False
