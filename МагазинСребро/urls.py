"""
URL configuration for МагазинСребро project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.http import HttpResponsePermanentRedirect

# Redirect marbaras.com to www.marbaras.com
def redirect_to_www(request):
    """Redirect non-www to www subdomain."""
    host = request.get_host().lower()
    if host.startswith('marbaras.com'):
        return HttpResponsePermanentRedirect(f"https://www.{host}{request.get_full_path()}")
    return None

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('ecommerce.urls')),
    path('accounts/', include('allauth.urls')),
    path('login/', lambda request: redirect('/accounts/login/')),
]

# Add redirect middleware for non-www to www (only in production)
if not settings.DEBUG:
    # This will be handled by middleware, but we can also add it here as a fallback
    pass

# Error handlers (only work when DEBUG=False)
handler404 = 'ecommerce.views.handler404'
handler500 = 'ecommerce.views.handler500'

# Serve static and media files in production (Railway doesn't have Nginx)
# Django will serve these files directly in production

# Serve static files (for Django admin and other static assets)
if settings.DEBUG:
    # In development, use staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
else:
    # In production, serve static files from STATIC_ROOT
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, serve media files through Django
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
