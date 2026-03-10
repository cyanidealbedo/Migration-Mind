# django_app/apps/core/apps.py

from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # This must match the actual python path to the app
    name = 'apps.core'
