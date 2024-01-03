from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("google/login/callback/", views.google_callback, name="google_callback"),
    path("google/login/", views.google_login, name="google_login"),
    path("line/login/callback/", views.line_callback, name="line_callback"),
    path("line/login/", views.line_login, name="line_login"),
]
