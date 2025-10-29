# ecommerce/utils/emailing.py
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template.loader import render_to_string

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
    # Prefer an explicit order email (e.g., shipping email), else fallback to user's email.
    recipient = getattr(order, "email", None) or getattr(getattr(order, "user", None), "email", None)
    if not recipient:
        log.warning("Order email skipped, no recipient for order #%s", order.id)
        return False

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@example.com"

    # Avoid N+1 when templates access item.product
    items = order.items.select_related("product").all()

    ctx = {"order": order, "items": items, "base_url": base_url}
    try:
        subject = f"Your Marbaras order #{order.id} 👑"
        text = render_to_string("emails/order_confirmation.txt", ctx)
        html = render_to_string("emails/order_confirmation.html", ctx)

        msg = EmailMultiAlternatives(subject, text, from_email, [recipient])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

        if notify_admin:
            total = getattr(order, "total_price", None)
            customer = getattr(order, "full_name", None) or getattr(order, "user", None)
            mail_admins(
                subject=f"New order #{order.id}",
                message=f"Total: {total}\nCustomer: {customer}\nOrder URL: {base_url}/admin/",
                fail_silently=True,
            )
        return True
    except Exception as e:
        log.exception("Failed to send order email for #%s: %s", order.id, e)
        return False
