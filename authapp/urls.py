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
    path("songs/", views.song_list, name="song_list"),  # map the song_list view
    path("songs/<int:pk>/", views.song_list, name="song_detail"),
    path("upload_song/", views.upload_song, name="upload_song"),  # Url for upload song
    path("all_songs/", views.all_songs_view, name="all_songs"),
]
