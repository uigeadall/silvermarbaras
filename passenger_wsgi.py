import os, sys

# ✅ Add your project path
BASE_DIR = "/home/ivkxjde0/marbaras.com/"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "МагазинСребро.settings")

# ✅ Load Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
