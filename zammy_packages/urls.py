from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        path("users/", include("zammy_packages.account.urls", namespace="users")),
    ]
