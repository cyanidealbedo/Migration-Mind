# django_app/migrationmind/settings.py
import os
from pathlib import Path
import environ

env = environ.Env(DEBUG=(bool, True))
BASE_DIR = Path(__file__).resolve().parent.parent

# .env loading
env_in_app  = os.path.join(BASE_DIR, '.env')
env_in_root = os.path.join(BASE_DIR.parent, '.env')
if os.path.exists(env_in_app):
    environ.Env.read_env(env_in_app)
    print(f"✅ Loaded .env from: {env_in_app}")
elif os.path.exists(env_in_root):
    environ.Env.read_env(env_in_root)
    print(f"✅ Loaded .env from: {env_in_root}")
else:
    print("❌ WARNING: No .env file found!")

SECRET_KEY    = env('DJANGO_SECRET_KEY', default='django-insecure-development-key-change-in-prod')
DEBUG         = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0'])

# Allow Azure App Service health check
CSRF_TRUSTED_ORIGINS = [
    'https://mm-django-app.azurewebsites.net',
    'http://mm-django-app.azurewebsites.net',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # ← RIGHT after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'migrationmind.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'apps', 'core', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ── Static files — WhiteNoise serves these in production ──
STATIC_URL  = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'apps', 'core', 'static')]

# WhiteNoise: compressed + cached static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Azure Service Bus ──
SERVICE_BUS_CONNECTION_STRING = env('SERVICE_BUS_CONNECTION_STRING', default=None)
SERVICE_BUS_QUEUE_NAME        = env('SERVICE_BUS_QUEUE_NAME', default='assessment-jobs')

# ── Azure AI Content Safety ──
CONTENT_SAFETY_ENDPOINT = env('CONTENT_SAFETY_ENDPOINT', default=None)
CONTENT_SAFETY_KEY      = env('CONTENT_SAFETY_KEY',      default=None)

# ── Azure Application Insights ──
APPLICATIONINSIGHTS_CONNECTION_STRING = env('APPLICATIONINSIGHTS_CONNECTION_STRING', default=None)

# ── Azure Key Vault (optional) ──
KEY_VAULT_URL = env('KEY_VAULT_URL', default=None)

if KEY_VAULT_URL and not DEBUG:
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        kv_client = SecretClient(vault_url=KEY_VAULT_URL, credential=DefaultAzureCredential())
        _kv_map = {
            'django-secret-key':                     'SECRET_KEY',
            'service-bus-connection-string':         'SERVICE_BUS_CONNECTION_STRING',
            'content-safety-endpoint':               'CONTENT_SAFETY_ENDPOINT',
            'content-safety-key':                    'CONTENT_SAFETY_KEY',
            'applicationinsights-connection-string': 'APPLICATIONINSIGHTS_CONNECTION_STRING',
        }
        for secret_name, setting_name in _kv_map.items():
            try:
                val = kv_client.get_secret(secret_name).value
                if setting_name:
                    import sys
                    setattr(sys.modules[__name__], setting_name, val)
            except Exception:
                pass
        print(f"✅ Key Vault secrets loaded from {KEY_VAULT_URL}")
    except Exception as e:
        print(f"⚠️  Key Vault load failed (non-fatal): {e}")

if APPLICATIONINSIGHTS_CONNECTION_STRING:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING)
        print("✅ Azure Monitor / App Insights configured")
    except ImportError:
        print("⚠️  azure-monitor-opentelemetry not installed — skipping")
    except Exception as e:
        print(f"⚠️  App Insights init failed (non-fatal): {e}")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'apps.core': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}
