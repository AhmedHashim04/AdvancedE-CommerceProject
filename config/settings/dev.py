from .base import *
from decouple import config  



# ----------- DATABASE -----------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# ----------- HOSTS & CORS -----------

ALLOWED_HOSTS = ['*']

# ----------- CACHE -----------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-sample-cache',
    }
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': '/var/tmp/django_cache',
#     }
# }

# SESSION_ENGINE = 'django.contrib.sessions.backends.'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # مدة الحياة بالثواني (هنا أسبوع)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # لو True يتم المسح عند غلق المتصفح

# ----------- TOOLBAR -----------

# ----------- CELERY -----------
