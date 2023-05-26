from django.urls import path
from techsupport.views import user_login, user_logout, home

urlpatterns = [
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("", home, name="home"),
]
