"""Custom middleware for the ecommerce app."""
from django.http import HttpResponsePermanentRedirect


class WWWRedirectMiddleware:
    """Redirect non-www to www subdomain."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        # Redirect marbaras.com to www.marbaras.com
        if host == 'marbaras.com':
            return HttpResponsePermanentRedirect(
                f"https://www.marbaras.com{request.get_full_path()}"
            )
        return self.get_response(request)

