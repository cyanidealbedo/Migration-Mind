# django_app/migrationmind/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns =[
    path('admin/', admin.site.urls),
    # Route all other URLs to our core app
    path('', include('apps.core.urls')),
]
