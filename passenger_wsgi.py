"""
Phusion Passenger WSGI configuration for Marbaras.

This file is used when deploying on shared hosting with Passenger support
(DreamHost, A2 Hosting, SiteGround, etc.) or VPS with Passenger + Nginx.

For Docker/Railway/Render deployments, use the standard wsgi.py instead.
"""
import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "МагазинСребро.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
