from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django import forms
from . import TicketCreateForm, TicketForm
from django.http import Http404
from .models import Ticket

from .models import SupportTicket

# Home page view for user and field coordinators/managers


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = "account_login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name="manager").exists():
            # get all tickets for the manager"s assigned region or cluster
            context["tickets"] = SupportTicket.objects.filter(
                region=self.request.user.region)
        else:
            # get tickets only for the current user
            context["tickets"] = SupportTicket.objects.filter(
                user=self.request.user)
        return context

# Login view


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


def base(request):
    return render(request, "accounts/base.html")


# Create support ticket view

@login_required
def create_ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.created_at = timezone.now()
            ticket.save()
            messages.success(request, "Your ticket has been created.")
            return redirect("ticket_detail", pk=ticket.pk)
        else:
            messages.error(request, "There was an error creating your ticket.")
    else:
        form = TicketForm()
    return render(request, "support_ticket/create_ticket.html", {"form": form})

# Support ticket detail view for user and field coordinators/managers


@login_required(login_url="account_login")
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    if request.user.groups.filter(name="manager").exists():
        # only allow manager to view tickets in their assigned region or cluster
        if ticket.region != request.user.region:
            messages.error(
                request, "You are not authorized to view this ticket.")
            return redirect("home")
    else:
        # only allow user to view their own tickets
        if ticket.user != request.user:
            messages.error(
                request, "You are not authorized to view this ticket.")
            return redirect("home")
    return render(request, "support_ticket/ticket_detail.html", {"ticket": ticket})

# Support ticket update view for technician and admin


@login_required(login_url="account_login")
def update_ticket(request, pk):
    ticket = SupportTicket.objects.get(pk=pk)
    if request.user.groups.filter(name="technician").exists() or request.user.is_superuser:
        if request.method == "POST":
            status = request.POST.get("status")
            priority = request.POST.get("priority")
            # update ticket status and priority
            ticket.status = status
            ticket.priority = priority
            ticket.save()
            messages.success(request, "Ticket updated successfully!")
            return redirect("ticket_detail", pk=pk)
        return render(request, "support_ticket/update_ticket.html", {"ticket": ticket})
    else:
        messages.error(
            request, "You are not authorized to update this ticket.")
        return redirect("home")

# Support ticket list view for technician and admin


@login_required(login_url="account_login")
def ticket_list(request):
    if request.user.groups.filter(name="technician").exists() or request.user.is_superuser:
        tickets = SupportTicket.objects.all()
        return render(request, "support_ticket/ticket_list.html", {"tickets": tickets})
    else:
        messages.error(
            request, "You do not have permission to access this page")
        return redirect("home")


# Support ticket details view

@login_required(login_url="account_login")
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    if request.user.groups.filter(name="user").exists() and request.user != ticket.reported_by:
        messages.error(request, "You are not authorized to view this ticket")
        return redirect("home")
    return render(request, "support_ticket/ticket_detail.html", {"ticket": ticket})


# Edit support ticket view for technician and admin


def edit_ticket(request, ticket_id):
    # Retrieve the ticket object with the given ID
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # If this is a GET request, render the ticket form with the existing ticket data
    if request.method == "GET":
        form = TicketForm(instance=ticket)
        return render(request, "support_ticket/edit_ticket.html", {"form": form})

    # If this is a POST request, validate the submitted form data and update the ticket
    form = TicketForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        return redirect("ticket_detail", ticket_id=ticket.id)

    # If the form data is invalid, re-render the form with the error messages
    return render(request, "support_ticket/edit_ticket.html", {"form": form})


# Support ticket detail view for technician and superuser

@login_required(login_url="account_login")
def ticket_detail(request, ticket_id):
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        raise Http404("Ticket does not exist")

    # check if user is authorized to view this ticket
    if not (request.user.groups.filter(name="technician").exists() or request.user.is_superuser or request.user == ticket.user):
        messages.error(request, "You are not authorized to view this ticket")
    return redirect("ticket_list")

    if request.method == "POST":
        form = TicketUpdateForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        messages.success(request, "Ticket has been updated")
        return redirect("ticket_detail", ticket_id=ticket.id)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, "support_ticket/ticket_detail.html", {"ticket": ticket, "form": form})


# Support ticket list view for users and field coordinators/managers
@login_required(login_url="account_login")
def user_ticket_list(request):
    if not (request.user.groups.filter(name="manager").exists() or request.user.is_superuser):
        tickets = SupportTicket.objects.filter(user=request.user)
    else:
        tickets = SupportTicket.objects.all()
        return render(request, "support_ticket/user_ticket_list.html", {"tickets": tickets})


# Support ticket detail view for users field coordinators/managers/superusers
@login_required(login_url="account_login")
def user_ticket_detail(request, ticket_id):
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        raise Http404("Ticket does not exist")

    # check if user is authorized to view this ticket
    if not (request.user.groups.filter(name="manager").exists() or request.user.is_superuser or request.user == ticket.user):
        messages.error(request, "You are not authorized to view this ticket")
    return redirect("user_ticket_list")
    return render(request, "support_ticket/user_ticket_detail.html", {"ticket": ticket})
