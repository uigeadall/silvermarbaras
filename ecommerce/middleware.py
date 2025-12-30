"""Custom middleware for the ecommerce app."""
from django.http import HttpResponsePermanentRedirect
from django.conf import settings


class WWWRedirectMiddleware:
    """Redirect non-www to www subdomain (enabled by default in production, can be disabled via env)."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if www redirect is enabled
        # Default: enabled in production (not DEBUG), disabled in development
        import os
        redirect_to_www_env = os.environ.get('REDIRECT_TO_WWW', '').lower()
        
        # If explicitly set, use that value
        if redirect_to_www_env:
            redirect_to_www = redirect_to_www_env == 'true'
        else:
            # Default: redirect in production (when not DEBUG)
            redirect_to_www = not settings.DEBUG
        
        if not redirect_to_www:
            return self.get_response(request)
        
        host = request.get_host().lower()

        # Redirect non-www to www
        if host == 'marbaras.com':
            return HttpResponsePermanentRedirect(
                f"https://www.marbaras.com{request.get_full_path()}"
            )
        return self.get_response(request)

