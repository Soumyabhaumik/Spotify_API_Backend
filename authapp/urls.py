from django.urls import path
from . import views

app_name = "auth"  # Must be here for namespacing

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),  # <== This defines 'auth:signup'
    path("home/", views.home_view, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("google_login/", views.google_login, name="google_login"),  # Add this
    path("google_callback/", views.google_callback, name="google_callback"),  # Add this
]
