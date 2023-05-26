from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from django.db.models import Q, Avg
from django.views.generic import ListView
from django.views import View
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error_message = "Invalid username or password"
    else:
        error_message = None
    return render(request, "accounts/login.html", {"error_message": error_message})


def user_logout(request):
    logout(request)
    return render(request, "accounts/logout.html")


@login_required
def home(request):
    user = request.user
    template_name = "home.html"
    return render(request, template_name)
