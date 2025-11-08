from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# -------------------------
# Env helpers
# -------------------------
def env(key: str, default=None):
    return os.environ.get(key, default)

def env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def env_list(key: str, default=None, sep=","):
    val = os.environ.get(key)
    if not val:
        return default or []
    return [item.strip() for item in val.split(sep) if item.strip()]

# -------------------------
# Core
# -------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)

# Warn if using insecure default SECRET_KEY in production
if not DEBUG and SECRET_KEY == "dev-insecure-change-me":
    import warnings
    warnings.warn(
        "SECRET_KEY is using the default insecure value. "
        "Set DJANGO_SECRET_KEY in your environment variables!",
        UserWarning
    )

# -------------------------
# Hosts & CSRF (supports ngrok, loca.lt, cloudflare)
# -------------------------
NGROK_HOST = env("NGROK_HOST", "").strip()  # optional single ngrok host

if DEBUG:
    # In development, allow everything (to avoid DisallowedHost)
    ALLOWED_HOSTS = ["*"]
else:
    base_allowed = {"localhost", "127.0.0.1"}
    ALLOWED_HOSTS = sorted(base_allowed.union(set(env_list("DJANGO_ALLOWED_HOSTS", []))))

# Default CSRF origins
default_csrf = {
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.ngrok-free.app",
    "https://*.loca.lt",              # LocalTunnel
    "https://*.trycloudflare.com",    # Cloudflare Tunnel (optional)
}
CSRF_TRUSTED_ORIGINS = sorted(default_csrf.union(set(env_list("CSRF_TRUSTED_ORIGINS", []))))

# Add explicitly defined ngrok/localtunnel hosts from .env
if NGROK_HOST:
    if ALLOWED_HOSTS != ["*"] and NGROK_HOST not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(NGROK_HOST)
    origin = f"https://{NGROK_HOST}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Optional: list of tunnel hosts in .env (e.g., TUNNEL_HOSTS=b18e6d72e658.ngrok-free.app,floppy-webs-lie.loca.lt)
for host in env_list("TUNNEL_HOSTS", []):
    if ALLOWED_HOSTS != ["*"] and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
    origin = f"https://{host}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

SITE_ID = int(env("DJANGO_SITE_ID", "1"))

# -------------------------
# Applications
# -------------------------
INSTALLED_APPS = [
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Allauth Authentication
    "allauth",
    "allauth.account",

    # Local App
    "ecommerce.apps.EcommerceConfig",
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "МагазинСребро.urls"
WSGI_APPLICATION = "МагазинСребро.wsgi.application"


# -------------------------
# Templates
# -------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "ecommerce.context_processors.breadcrumbs",
                "ecommerce.context_processors.cart_count",
            ],
        },
    },
]

# -------------------------
# Database (MySQL)
# -------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQL_DATABASE", "silvershop"),
        "USER": env("MYSQL_USER", "root"),
        "PASSWORD": env("MYSQL_PASSWORD", ""),
        "HOST": env("MYSQL_HOST", "localhost"),
        "PORT": env("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES', time_zone='+00:00'",
            "charset": "utf8mb4",
        },
        "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", "0")),  # Connection pooling (0 = disabled)
        "ATOMIC_REQUESTS": env_bool("DB_ATOMIC_REQUESTS", False),
    }
}

# -------------------------
# Auth / Allauth
# -------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Session settings
SESSION_COOKIE_AGE = int(env("SESSION_COOKIE_AGE", "1209600"))  # 2 weeks default
SESSION_SAVE_EVERY_REQUEST = env_bool("SESSION_SAVE_EVERY_REQUEST", False)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool("SESSION_EXPIRE_AT_BROWSER_CLOSE", False)

# CSRF settings
CSRF_COOKIE_AGE = int(env("CSRF_COOKIE_AGE", "31449600"))  # 1 year default
CSRF_COOKIE_HTTPONLY = True
CSRF_FAILURE_VIEW = "django.views.csrf.csrf_failure"

ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_ADAPTER = "ecommerce.adapters.CustomAccountAdapter"


# -------------------------
# I18N / TZ
# -------------------------
LANGUAGE_CODE = "bg"
TIME_ZONE = "Europe/Sofia"
USE_I18N = True
USE_TZ = True

# -------------------------
# Static & Media
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Static files finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = int(env("FILE_UPLOAD_MAX_MEMORY_SIZE", "2621440"))  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = int(env("DATA_UPLOAD_MAX_MEMORY_SIZE", "2621440"))  # 2.5 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(env("DATA_UPLOAD_MAX_NUMBER_FIELDS", "1000"))

# -------------------------
# Email
# -------------------------
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "sales@marbaras.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [("Site Admin", env("ADMIN_EMAIL", "admin@example.com"))]

EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "sandbox.smtp.mailtrap.io")
EMAIL_PORT = int(env("EMAIL_PORT", "2525"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = int(env("EMAIL_TIMEOUT", "30"))

# -------------------------
# Stripe
# -------------------------
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", "")

# -------------------------
# Security (production)
# -------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    
    # Support for reverse proxy (nginx, etc.)
    USE_X_FORWARDED_HOST = env_bool("USE_X_FORWARDED_HOST", True)
    USE_X_FORWARDED_PORT = env_bool("USE_X_FORWARDED_PORT", True)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------
# Logging
# -------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if not DEBUG else "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"] + (["file"] if not DEBUG else []),
        "level": "INFO" if not DEBUG else "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"] + (["file"] if not DEBUG else []),
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"] + (["file"] if not DEBUG else []),
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"] + (["file"] if not DEBUG else []),
            "level": "WARNING",
            "propagate": False,
        },
        "django.core.mail": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "ecommerce": {
            "handlers": ["console"] + (["file"] if not DEBUG else []),
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "stripe": {
            "handlers": ["console"] + (["file"] if not DEBUG else []),
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# -------------------------
# Defaults
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
