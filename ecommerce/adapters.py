from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse
import logging

log = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)

        if commit:
            user.save()
        return user
    
    def send_mail(self, template_prefix, email, context):
        """Override send_mail to use custom password reset email template."""
        # For password reset emails, use our custom function
        if template_prefix == 'account/email/password_reset_key':
            from .utils.emailing import send_password_reset_email
            
            # Get user from context
            user = context.get('user')
            if not user:
                # Fallback to default if no user
                return super().send_mail(template_prefix, email, context)
            
            # Build reset URL from key
            key = context.get('key', '')
            if not key:
                # Fallback to default if no key
                return super().send_mail(template_prefix, email, context)
            
            # Get base_url from request
            request = context.get('request')
            if request:
                try:
                    base_url = request.build_absolute_uri('/').rstrip('/')
                except Exception:
                    base_url = 'https://www.marbaras.com'
            else:
                base_url = 'https://www.marbaras.com'
            
            # Build reset URL
            try:
                reset_url = request.build_absolute_uri(
                    reverse('account_reset_password_from_key', kwargs={'uidb36': context.get('uid'), 'key': key})
                ) if request else f"{base_url}/accounts/password/reset/key/{key}/"
            except Exception:
                reset_url = f"{base_url}/accounts/password/reset/key/{key}/"
            
            # Send custom email
            try:
                send_password_reset_email(user, reset_url, base_url)
                log.info("Custom password reset email sent to %s", email)
                return  # Don't call super() if we successfully sent our custom email
            except Exception as e:
                log.exception("Failed to send custom password reset email, falling back to default: %s", e)
                # Fallback to default email
                return super().send_mail(template_prefix, email, context)
        
        # For all other emails, use default behavior
        return super().send_mail(template_prefix, email, context)