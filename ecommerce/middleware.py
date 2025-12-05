"""Custom middleware for the ecommerce app."""
from django.http import HttpResponsePermanentRedirect


class WWWRedirectMiddleware:
    """Redirect non-www to www subdomain (optional, can be disabled via env)."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if www redirect is enabled (default: disabled to allow both domains)
        import os
        redirect_to_www = os.environ.get('REDIRECT_TO_WWW', 'false').lower() == 'true'
        
        if not redirect_to_www:
            return self.get_response(request)
        
        host = request.get_host().lower()

        if host == 'marbaras.com':
            return HttpResponsePermanentRedirect(
                f"https://www.marbaras.com{request.get_full_path()}"
            )
        return self.get_response(request)

