from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from django.contrib.auth.models import User

from .forms import TicketCreateForm, TicketForm, TicketUpdateForm
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket


# Home page view for user/coach and field coordinators/managers

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = "account_login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name="manager").exists():
            # get all tickets for the manager's assigned region or cluster
            context["tickets"] = SupportTicket.objects.filter(
                region=self.request.user.region)
        else:
            # get tickets only for the current user/coach
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
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = SupportTicket(
                user=request.user,
                category=form.cleaned_data["category"],
                sub_category=form.cleaned_data["sub_category"],
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                priority=form.cleaned_data["priority"],
                region=request.user.region,
                centre=form.cleaned_data["centre"],
                country=form.cleaned_data["country"],
                created_at=timezone.now(),
            )
            ticket.save()
            messages.success(request, "Your ticket has been created.")
            return redirect("ticket_detail", ticket_id=ticket.id)
        else:
            messages.error(request, "There was an error creating your ticket.")
    else:
        form = TicketCreateForm()
    return render(request, "support_ticket/create_ticket.html", {"form": form})


# Support ticket detail view for user/coach and field coordinators/managers

@login_required(login_url="account_login")
def ticket_detail(request, ticket_id):
    # Get the support ticket object with the given ticket_id or return a 404 error if not found
    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    # Check if the user/coach has permission to view the ticket
    if request.user == ticket.user or request.user.region == ticket.region or request.user.groups.filter(name="manager").exists():
        return render(request, "support_ticket/ticket_detail.html", {"ticket": ticket})
    else:
        messages.error(
            request, "You do not have permission to view this ticket.")
        return redirect("home")


# A function to check if the coach belongs to the manager group
def is_manager(user):
    return user.groups.filter(name='manager').exists()

# A view that displays the dashboard for managers only
# It uses the @user_passes_test decorator to ensure that only managers can access this view
# It gets all support tickets that belong to the manager's assigned region/cluster and passes them to the template

@user_passes_test(is_manager)
def manager_dashboard(request):
    tickets = SupportTicket.objects.filter(region=request.user.region)
    return render(request, "support_ticket/manager_dashboard.html", {"tickets": tickets})


# Edit support ticket view for technician and admin
@login_required(login_url="account_login")
def edit_ticket(request, ticket_id):
    # Retrieve the ticket object with the given ID
    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    # If this is a GET request, render the ticket form with the existing ticket data
    if request.method == "GET":
        form = TicketCreateForm(instance=ticket)
        return render(request, "support_ticket/edit_ticket.html", {"form": form})

    # If this is a POST request, validate the submitted form data and update the ticket
    form = TicketCreateForm(request.POST, instance=ticket)
    if form.is_valid():
        ticket = form.save(commit=False)
        ticket.updated_at = timezone.now()
        ticket.save()
        return redirect("ticket_detail", ticket_id=ticket.id)

    # If the form data is invalid, re-render the form with the error messages
    return render(request, "support_ticket/edit_ticket.html", {"form": form})


@login_required(login_url="account_login")
def update_ticket(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)

    # Check if the user/coach is authorized to update the ticket
    if request.user.groups.filter(name="technician").exists() or request.user.is_superuser:
        # If it is a POST request, update the ticket with the new data
        if request.method == "POST":
            form = TicketUpdateForm(request.POST, instance=ticket)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.save()
                messages.success(request, "Ticket updated successfully!")
                return redirect("ticket_detail", pk=pk)
        else:
            # If it is a GET request, display the ticket update form
            form = TicketUpdateForm(instance=ticket)
        return render(request, "support_ticket/update_ticket.html", {"form": form, "ticket": ticket})
    else:
        messages.error(
            request, "You are not authorized to update this ticket.")
        return redirect("home")


#Support ticket list view for technician and admin


@login_required(login_url="account_login")
@user_passes_test(lambda user: user.groups.filter(name='technician').exists() or user.is_superuser)
def ticket_list(request):
    tickets = SupportTicket.objects.all()
    return render(request, "support_ticket/ticket_list.html", {"tickets": tickets})


#Support ticket detail view for technician and superuser

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


# Support ticket list view for users/coaches and field coordinators/managers
@login_required(login_url="account_login")
def coach_ticket_list(request):
    if request.user.groups.filter(name="manager").exists() or request.user.is_superuser:
        tickets = SupportTicket.objects.all()
    else:
        tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, "support_ticket/coach_ticket_list.html", {"tickets": tickets})


# Support ticket detail view for users/coaches, field coordinators/managers, and superusers
@login_required(login_url="account_login")
def coach_ticket_detail(request, ticket_id):
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        raise Http404("Ticket does not exist")

    # check if user is authorized to view this ticket
    if not (request.user.groups.filter(name="manager").exists() or request.user.is_superuser or request.user == ticket.user):
        messages.error(request, "You are not authorized to view this ticket")
        return redirect("coach_ticket_list")
    return render(request, "support_ticket/coach_ticket_detail.html", {"ticket": ticket})


#Admin dashboard view

@login_required(login_url="account_login")
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    user = request.user
    total_tickets = SupportTicket.objects.count()
    open_tickets = SupportTicket.objects.filter(status="Open").count()
    closed_tickets = SupportTicket.objects.filter(status="Closed").count()
    tech_users = User.objects.filter(groups__name="technician").count()
    return render(request, "support_ticket/admin_dashboard.html", {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "tech_users": tech_users
    })
