from decouple import config  
from pathlib import Path
from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST', default='localhost'),
        'PORT': config('POSTGRES_PORT', default='5432'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1", 
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

LOGGING_DIR = BASE_DIR / 'logs'
LOGGING_DIR.mkdir(exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # خليه False علشان ما يعطّل لوجات Django الأساسية
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',  # مستوى اللوجات اللي هتتسجل
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR / 'project.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # لوجر مخصص لتطبيق معين مثلاً
        # 'myapp': {
        #     'handlers': ['file'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
    }
}


MIDDLEWARE += [
    'project.rate_limit_logging.RatelimitLoggingMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
    'project.middleware.FullCPUMeasureMiddleware',
    'project.middleware.CPUMeasureMiddleware',
    'project.middleware.TimerMiddleware',
]

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"


# CELERY_BROKER_URL = config('REDIS_URL')
# CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'


# CELERY_BROKER_URL = config('REDIS_URL')  # بدون default هنا

# if not CELERY_BROKER_URL:
#     raise Exception("REDIS_URL is not set. Add it to Railway environment variables.")

# CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
