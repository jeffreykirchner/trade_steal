import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True #os.environ.get('DEBUG', False)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = 'main/static/'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split()

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

hostname = os.environ['DBHOST']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DBNAME'],
        'HOST': hostname + ".postgres.database.azure.com",
        'USER': os.environ['DBUSER'],
        'PASSWORD': os.environ['DBPASS'],
        'OPTIONS': {'sslmode': 'require'},
    },
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ['REDIS'])],
        },
    },
}

#logging, log both to console and to file log at the INFO level
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'info_format': {
            'format': '%(levelname)s %(asctime)s %(module)s: %(message)s'
            }
        },
    'handlers': {
        'console': {
            'level':'INFO',
            'class': 'logging.StreamHandler',
        },
       'logfile': {        
           'level':'INFO', 
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': os.environ['LOG_LOCATION'],
           'maxBytes': 10485760,           #10 mb
           'backupCount' : 5,
           'formatter' : 'info_format',
           'delay': True,
       },
    },
    'loggers': {
        'django': {
            'handlers':['console','logfile'],
            'propagate': True,
            'level':'INFO',
        },
        'django.db.backends': {
            'handlers': ['console','logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        'main': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',           
        },
        'channels': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',           
        },
    },
}
