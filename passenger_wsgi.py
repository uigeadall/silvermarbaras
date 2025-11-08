"""
Phusion Passenger WSGI configuration for Marbaras.

This file is used when deploying on shared hosting with Passenger support
(DreamHost, A2 Hosting, SiteGround, etc.) or VPS with Passenger + Nginx.

For Docker/Railway/Render deployments, use the standard wsgi.py instead.
"""
import os
import sys

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add project directory to Python path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "МагазинСребро.settings")

# Load Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
