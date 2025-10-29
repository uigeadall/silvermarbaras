# ecommerce/signals.py
from django.dispatch import Signal, receiver
from django.db import transaction
from allauth.account.signals import user_signed_up

from .utils.emailing import (
    send_welcome_email,
    send_order_confirmation_email,
)

# Custom signals your views will emit
user_registered = Signal()   # args: user, request
order_submitted = Signal()   # args: order, request, base_url (optional)


@receiver(user_signed_up, dispatch_uid="ecommerce_welcome_allauth_v1")
def send_welcome_allauth(sender, request, user, **kwargs):
    """Welcome email for allauth signups."""
    base_url = request.build_absolute_uri('/').rstrip('/')
    transaction.on_commit(lambda: send_welcome_email(user, base_url))


@receiver(user_registered, dispatch_uid="ecommerce_welcome_custom_v1")
def send_welcome_custom(sender, user, request=None, **kwargs):
    """Welcome email for your custom register_view."""
    base_url = request.build_absolute_uri('/').rstrip('/') if request else ""
    transaction.on_commit(lambda: send_welcome_email(user, base_url))


@receiver(order_submitted, dispatch_uid="ecommerce_order_confirmation_v1")
def send_order_confirmation(sender, order, request=None, base_url=None, **kwargs):
    """Order confirmation once Order + items are fully saved."""
    if not base_url and request is not None:
        base_url = request.build_absolute_uri('/').rstrip('/')
    transaction.on_commit(lambda: send_order_confirmation_email(order, base_url, notify_admin=True))
