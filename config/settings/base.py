"""
Django 5.1
"""

import os
from pathlib import Path
from decouple import config  

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ROOT_URLCONF = "project.urls"

WSGI_APPLICATION = "project.wsgi.application"

INSTALLED_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    'rest_framework.authtoken',   # ← أضفه هنا
    "rest_framework_simplejwt.token_blacklist", 
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "dj_rest_auth",
    "dj_rest_auth.registration",

    "apps.accounts", 
    "apps.home",
    "apps.contact",
    "apps.cart",
    "apps.checkout",
    "apps.orders",
    "apps.payments",
    "apps.reviews",
    "apps.store",
    "apps.promotions",
    "apps.notifications",
    
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
  

]

AUTH_USER_MODEL = "accounts.CustomUser"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            'client_id':config('GOOGLE_CLIENT_ID'),
            'secret':config('GOOGLE_CLIENT_SECRET'),
            "key": ""
        }
    }
}
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'my-app-auth'


SITE_ID = 1

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"]

}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,          # يعيد توكن جديد عند refresh
    "BLACKLIST_AFTER_ROTATION": True,       # يضيف القديم للـ blacklist بعد الدوران
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("SECRET_KEY"),              # أو مفتاح خاص
    "AUTH_HEADER_TYPES": ("Bearer",),
    # لو عايز تحقق من audience/issuer ممكن تضيفهم
}


LOGIN_REDIRECT_URL = '/' 
LOGOUT_REDIRECT_URL = "/"



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR /  "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # "project.context_module.global_context",
            ],
        },
    },
]


MIDDLEWARE = [
    'allauth.account.middleware.AccountMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ar', 'Arabic'),
    ('en', 'English'),
]


LOCALE_PATHS = [
    BASE_DIR / 'locale', 
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CART_SESSION_ID = "cart"



# ----------- STATIC & MEDIA -----------


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "mediafiles"



DEBUG = config("DEBUG", default=False, cast=bool)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'Modyex <%s>' % config('DEFAULT_FROM_EMAIL')
STORE_OWNER_EMAIL = config('STORE_OWNER_EMAIL')
SHIPPING_EMAIL = config('SHIPPING_EMAIL')

# ----------- SECURITY -----------

SECRET_KEY =config('SECRET_KEY',)
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips]
    INTERNAL_IPS += ["127.0.0.1", config('HOST')]  # fallback for local dev

    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: not request.path.startswith('/api/')
}
DEBUG_TOOLBAR_PANELS = [
    # باقي البانلز اللي تستخدمها
    # استثني 'debug_toolbar.panels.templates.TemplatesPanel'
]



# SECURE_HSTS_SECONDS = 31536000  # سنة
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# neoplasmo63@gmail.com
