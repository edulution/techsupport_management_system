from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from .views import *

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
