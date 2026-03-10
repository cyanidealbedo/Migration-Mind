# django_app/migrationmind/settings.py

import os
from pathlib import Path
import environ

# Initialize environ and set base directory
env = environ.Env(
    DEBUG=(bool, True)
)
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file if it exists
# --- NEW: Foolproof .env loading ---
env_in_app = os.path.join(BASE_DIR, '.env')
env_in_root = os.path.join(BASE_DIR.parent, '.env')

if os.path.exists(env_in_app):
    environ.Env.read_env(env_in_app)
    print(f"✅ Loaded .env from: {env_in_app}")
elif os.path.exists(env_in_root):
    environ.Env.read_env(env_in_root)
    print(f"✅ Loaded .env from: {env_in_root}")
else:
    print("❌ WARNING: No .env file found!")

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-development-key')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS =[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    
    # Local Apps
    'apps.core',
]

MIDDLEWARE =[
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'migrationmind.urls'

# --- NEW: Service Bus Variables ---
SERVICE_BUS_CONNECTION_STRING = env('SERVICE_BUS_CONNECTION_STRING', default=None)
SERVICE_BUS_QUEUE_NAME = env('SERVICE_BUS_QUEUE_NAME', default='assessment-jobs')

TEMPLATES =[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':[
            os.path.join(BASE_DIR, 'apps', 'core', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors':[
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'migrationmind.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

AUTH_PASSWORD_VALIDATORS =[
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS =[
    os.path.join(BASE_DIR, 'apps', 'core', 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'apps.core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
