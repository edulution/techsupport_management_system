from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from django.core.mail import send_mail
import ssl
import requests
import logging
import csv
import uuid
from .forms import (
    SupportTicketForm,
    SupportTicketUpdateForm,
    TicketResolutionForm,
    TicketAssignmentForm,
    TicketPriorityForm,
)
from .models import (
    Region,
    Centre,
    SubCategory,
    SupportTicket,
    Notification,
    UserProfile,
    User,
)
logger = logging.getLogger(__name__)


def user_login(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}!")
            return redirect("dashboard")
        else:
            error_message = "Invalid username or password"
            messages.warning(request, error_message)
    return render(request, "accounts/login.html", {"error_message": error_message})


def user_logout(request):
    logout(request)
    return render(request, "accounts/login.html")


@login_required
def dashboard(request):
    # Retrieve all support tickets
    tickets = SupportTicket.objects.all().order_by("-date_submitted")

    # Retrieve user's role using custom user model
    user_role = None
    user = User.objects.get(pk=request.user.pk)
    if user.is_super_admin():
        user_role = "super_admin"
    elif user.is_admin():
        user_role = "admin"
    elif user.is_manager():
        user_role = "manager"
    elif user.is_technician():
        user_role = "technician"
    elif user.is_user():
        user_role = "user"

    # Modify the tickets query based on the user's role
    if user_role == "super_admin":
        tickets = SupportTicket.objects.all()
    elif user_role == "admin":
        admin_country = request.user.country
        admin_region = request.user.region
        tickets = SupportTicket.objects.filter(
            Q(centre__region__country=admin_country) |
            Q(centre__region=admin_region)
        )
    elif user_role == "manager":
        manager_country = request.user.country
        manager_region = request.user.region
        tickets = SupportTicket.objects.filter(
            Q(centre__region__country=manager_country) |
            Q(centre__region=manager_region)
        )
    elif user_role == "technician":
        tickets = SupportTicket.objects.all()
    elif user_role == "user":
        user_centres = request.user.centres.all()
        tickets = SupportTicket.objects.filter(centre__in=user_centres)

    # Retrieve search parameters from the request
    search_query = request.GET.get("search_query", "").strip()
    status = request.GET.get("status")

    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(subcategory__name__icontains=search_query)
            | Q(centre__name__icontains=search_query)
            | Q(centre__region__name__icontains=search_query)
            | Q(submitted_by__username__icontains=search_query)
        )

    if status:
        tickets = tickets.filter(status=status)
    
    # retrieve ticket trends data
    ticket_trends = SupportTicket.objects.values("category__name").annotate(
        ticket_count=Count("id")
    )

    open_tickets_count = tickets.filter(status="Open").count()
    in_progress_tickets_count = tickets.filter(status="In Progress").count()
    resolved_tickets_count = tickets.filter(status="Resolved").count()

    def get_ticket_insights():
        common_ticket_trends = (
            SupportTicket.objects.values("category__name")
            .annotate(ticket_count=Count("id"))
            .order_by("-ticket_count")[:5]
        )
        frequent_issues = (
            SupportTicket.objects.values("subcategory__name")
            .annotate(ticket_count=Count("id"))
            .order_by("-ticket_count")[:5]
        )
        return {
            "common_ticket_trends": common_ticket_trends,
            "frequent_issues": frequent_issues,
        }

    tickets_per_page = 10

    paginator = Paginator(tickets, tickets_per_page)

    page = request.GET.get("page")

    try:
        paginated_tickets = paginator.page(page)
    except PageNotAnInteger:
        paginated_tickets = paginator.page(1)
    except EmptyPage:
        paginated_tickets = paginator.page(paginator.num_pages)

    if user_role == "technician" or "admin" or "super_admin":
        regions = Region.objects.all()
        centres = Centre.objects.all()
    else:
        manager_country = request.user.country
        regions = Region.objects.filter(country=manager_country)
        centres = Centre.objects.filter(region__country=manager_country)

    selected_regions = request.GET.getlist("region")
    selected_centres = request.GET.getlist("centre")

    if selected_regions:
        tickets = tickets.filter(centre__region__name__in=selected_regions)
    if selected_centres:
        tickets = tickets.filter(centre__name__in=selected_centres)

    context = {
        "user_role": user_role,
        "tickets": tickets,
        "open_tickets_count": open_tickets_count,
        "in_progress_tickets_count": in_progress_tickets_count,
        "resolved_tickets_count": resolved_tickets_count,
        "search_query": search_query,
        "ticket_trends": ticket_trends,
        "ticket_insights": get_ticket_insights(),
        "regions": regions,
        "centres": centres,
        "selected_regions": selected_regions,
        "selected_centres": selected_centres,
        "paginated_tickets": paginated_tickets,
    }

    return render(request, "dashboard.html", context)

@login_required
def export_tickets_csv(request):
    # Define the time period for which you want to extract data
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        tickets = SupportTicket.objects.filter(
            date_submitted__range=(start_date, end_date)
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="support_tickets.csv"'

        csv_writer = csv.writer(response)
        csv_writer.writerow(
            [
                "Ticket Number",
                "Date Submitted",
                "Status",
                "Priority",
                "Centre",
                "Submitted By",
                "Category",
                "Subcategory",
                "Description",
                "Title",
                "Resolution Notes",
                "Assigned To",
            ]
        )

        # Write ticket data to the CSV file
        for ticket in tickets:
            csv_writer.writerow(
                [
                    ticket.ticket_number,
                    ticket.date_submitted,
                    ticket.status,
                    ticket.priority,
                    ticket.centre.name,
                    ticket.submitted_by.username,
                    ticket.category.name,
                    ticket.subcategory.name,
                    ticket.description,
                    ticket.title,
                    ticket.resolution_notes,
                    ticket.assigned_to.username if ticket.assigned_to else "",
                ]
            )
        messages.success(request, "Support Ticket Data extracted successfully!")

        return response
    else:
        # Provide an empty queryset for the initial GET request
        tickets = SupportTicket.objects.none()

        return render(request, "support_ticket/export_tickets_csv.html")


@login_required
def profile(request):
    details = UserProfile.objects.filter(user=request.user.pk)
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None

    context = {
        "profile": profile,
        "details": details,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def ticket_details(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    form_resolution = None
    form_assignment = None
    form_priority = None
    from_email = settings.EMAIL_HOST_USER

    if request.user.role in ["technician", "admin", "super_admin"]:
        user_role = request.user.role
    else:
        user_role = None

    if request.method == "POST":
        if user_role in ["technician", "admin", "super_admin"]:
            form_assignment = TicketAssignmentForm(request.POST)
            if form_assignment.is_valid():
                assigned_to = form_assignment.cleaned_data["assigned_to"]
                ticket.assigned_to = assigned_to
                ticket.save()

                # Send an email when the ticket is assigned to a technician
                Notification.send_email_notification(ticket, Notification.MessageType.ASSIGNMENT)

                # Send the webhook message when a ticket is assigned
                Notification.send_webhook_notification(ticket, Notification.MessageType.ASSIGNMENT, request.user)

                messages.info(request, "Support ticket has been assigned.")
                return redirect("dashboard")

            form_resolution = TicketResolutionForm(request.POST, instance=ticket)
            if form_resolution.is_valid():
                ticket = form_resolution.save(commit=False)
                status = form_resolution.cleaned_data.get("status")
                if status == "Resolved":
                    ticket.status = "Resolved"
                    ticket.resolved_by = request.user

                    # Send an email when the ticket is resolved
                    Notification.send_email_notification(ticket, Notification.MessageType.RESOLUTION)

                    # Send the webhook message when the status changes to 'Resolved'
                    Notification.send_webhook_notification(ticket, Notification.MessageType.RESOLUTION, request.user)

                ticket.save()
                messages.info(request, "Support ticket status has been updated.")
                return redirect("dashboard")

            form_priority = TicketPriorityForm(request.POST, instance=ticket)
            if form_priority.is_valid():
                form_priority.save()

                messages.info(request, "Support ticket priority has been updated.")
                return redirect("dashboard")

        else:
            form = SupportTicketUpdateForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                messages.info(request, "Ticket description has been updated.")
                return redirect("dashboard")
    else:
        if user_role in ["technician", "admin", "super_admin"]:
            form_resolution = TicketResolutionForm(instance=ticket)
            form_assignment = TicketAssignmentForm()
            form_priority = TicketPriorityForm(instance=ticket)
        else:
            form = SupportTicketUpdateForm(instance=ticket)

    technicians = User.objects.filter(role="technician")

    context = {
        "ticket": ticket,
        "user_role": user_role,
        "form_resolution": form_resolution,
        "form_assignment": form_assignment,
        "form_priority": form_priority,
        "technicians": technicians,
    }

    return render(request, "support_ticket/ticket_details.html", context)


@login_required
def create_ticket(request):
    form = SupportTicketForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        support_ticket = form.save(commit=False)
        support_ticket.submitted_by = request.user
        support_ticket.save()

        # Send email notification
        Notification.send_email_notification(support_ticket, Notification.MessageType.TICKET_CREATION)

        # Send webhook notification
        Notification.send_webhook_notification(support_ticket, Notification.MessageType.TICKET_CREATION, request.user)

        messages.success(request, "Support ticket created successfully.")
        return redirect("dashboard")
    else:
        # Render the form with errors to display validation messages to the user
        context = {"form": form}
        return render(request, "support_ticket/create_ticket.html", context)


@login_required
def get_subcategories(request):
    category_id = request.GET.get("category_id")

    # Check if category_id is empty or not a valid UUID
    if not category_id:
        return JsonResponse({"subcategories": []})

    try:
        uuid.UUID(category_id)
    except (TypeError, ValueError):
        return JsonResponse({"subcategories": []})

    subcategories = SubCategory.objects.filter(category_id=category_id).values(
        "id", "name"
    )
    return JsonResponse({"subcategories": list(subcategories)})


@login_required
def all_tickets(request):
    user = request.user
    context = {}

    if user.is_user():
        # If the user is a regular user, filter tickets based on their assigned center
        user_tickets = user.submitted_issues.all()
        center = user.centres.first()
        
        # Fetch all tickets at the user's center (including those submitted by others)
        centre_tickets = SupportTicket.objects.filter(centre=center)
        
        # Combine the user's tickets and center tickets into a single queryset
        user_and_centre_tickets = user_tickets | centre_tickets
    elif user.is_technician():
        # If the user is a technician, they should only see tickets assigned to them and submitted by them
        user_and_centre_tickets = SupportTicket.objects.filter(assigned_to=user, submitted_by=user)
    elif user.is_manager():
        # If the user is a manager, they should only see tickets submitted by them
        user_and_centre_tickets = SupportTicket.objects.filter(submitted_by=user)
    elif user.is_admin():
        # If the user is an admin, they should only see tickets submitted by them
        user_and_centre_tickets = SupportTicket.objects.filter(submitted_by=user)
    else:
        # Handle other roles as needed
        user_and_centre_tickets = None

    total_tickets_count = user_and_centre_tickets.count()
    open_tickets_count = user_and_centre_tickets.filter(status="Open").count()
    in_progress_tickets_count = user_and_centre_tickets.filter(status="In Progress").count()
    resolved_tickets_count = user_and_centre_tickets.filter(status="Resolved").count()

    context.update({
        "user_and_centre_tickets": user_and_centre_tickets,
        "total_tickets_count": total_tickets_count,
        "open_tickets_count": open_tickets_count,
        "in_progress_tickets_count": in_progress_tickets_count,
        "resolved_tickets_count": resolved_tickets_count,
    })

    return render(request, "support_ticket/all_tickets.html", context)



# @login_required
# def settings_view(request):
#     """ settings view """

#     user = request.user
#     dark_mode_enabled = user.dark_mode_enabled

#     if request.method == 'POST':
#         dark_mode_enabled = request.POST.get('dark_mode_enabled') == 'on'
#         user.dark_mode_enabled = dark_mode_enabled
#         user.save()
#         return redirect('settings')

#     context = {
#         'dark_mode_enabled': dark_mode_enabled,
#     }
#     return render(request, 'support_ticket/settings.html', context)


@login_required
def assign_ticket(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    if request.method == "POST":
        technician_id = request.POST.get("technician_id")
        technician = User.objects.get(id=technician_id)
        ticket.resolved_by = technician
        ticket.save()
        messages.success(request, "Ticket assigned to technician successfully.")
        return redirect("ticket_details", ticket_id=ticket_id)
    else:
        technicians = User.objects.filter(groups__name="technician")
        context = {
            "ticket": ticket,
            "technicians": technicians,
        }
        return render(request, "support_ticket/assign_ticket.html", context)


def open_tickets(request):
    # Retrieve open tickets from the database
    tickets = SupportTicket.objects.filter(status="Open")
    context = {"tickets": tickets}
    return render(request, "support_ticket/open_tickets.html", context)


def resolved_tickets(request):
    # Retrieve resolved tickets from the database
    tickets = SupportTicket.objects.filter(status="Resolved")
    context = {"tickets": tickets}
    return render(request, "support_ticket/resolved_tickets.html", context)


def tickets_in_progress(request):
    tickets = SupportTicket.objects.filter(status="In Progress")
    return render(
        request, "support_ticket/tickets_in_progress.html", {"tickets": tickets}
    )
