from .base import *

# Define local settings

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [f"redis://:{os.getenv('REDIS_PASSWORD', 'changeme')}@{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}"],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', 'changeme')}@{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}/0",
        "TIMEOUT": 3600,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}


DEBUG = True
STATICFILES_DIRS = []

ALLOWED_HOSTS = ['*']

