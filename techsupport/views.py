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
import json
import requests
import logging
import csv
import uuid
from .forms import (
    SupportTicketForm,
    SupportTicketUpdateForm,
    TicketResolutionForm,
    TicketAssignmentForm,
)
from .models import (
    Country,
    Region,
    Centre,
    Category,
    SubCategory,
    SupportTicket,
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
def password_reset_complete(request):
    messages.success(request, "Your password has been reset successfully!")
    return redirect('login')


@login_required
def dashboard(request):
    tickets = SupportTicket.objects.all().order_by("-date_submitted")

    # Retrieve ticket trends data
    ticket_trends = SupportTicket.objects.values("category__name").annotate(
        ticket_count=Count("id")
    )

    user_role = None
    if request.user.groups.filter(
        name__in=["technician", "admin", "super_admin"]
    ).exists():
        user_role = "technician_or_above"

    elif request.user.groups.filter(name="manager").exists():
        user_role = "manager"

    if user_role != "technician_or_above":
        tickets = tickets.filter(submitted_by=request.user)

    # Retrieve search parameters from the request
    search_query = request.GET.get("search_query", "").strip()
    status = request.GET.get("status")

    if search_query:
        # Use Q objects for searching across multiple fields with OR condition
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
            # 'potential_solutions': potential_solutions,
        }

        # Retrieve the number of tickets per page (you can adjust this as needed)

    tickets_per_page = 10

    # Create a Paginator instance
    paginator = Paginator(tickets, tickets_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get("page")

    try:
        # Get the tickets for the requested page
        paginated_tickets = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        paginated_tickets = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), show the last page
        paginated_tickets = paginator.page(paginator.num_pages)

    if user_role == "technician_or_above":
        # Fetch all regions and centres for technicians and admins
        regions = Region.objects.all()
        centres = Centre.objects.all()
    else:
        # Retrieve the regions and centres for the manager filter
        manager_country = request.user.country
        regions = Region.objects.filter(country=manager_country)
        centres = Centre.objects.filter(region__country=manager_country)

    # Retrieve the selected regions and centres from the request
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
    user_role = None
    form_resolution = None
    form_assignment = None

    if request.user.groups.filter(
        name__in=["technician", "admin", "super_admin"]
    ).exists():
        user_role = "technician_or_above"

    if request.method == "POST":
        if user_role == "technician_or_above":
            # Check if the form for ticket assignment is submitted
            form_assignment = TicketAssignmentForm(request.POST)
            if form_assignment.is_valid():
                assigned_to = form_assignment.cleaned_data["assigned_to"]
                ticket.assigned_to = assigned_to
                ticket.save()
                
                # Send the webhook message when a ticket is assigned
                send_assignment_webhook(ticket.title, ticket.centre.name, assigned_to.username)
                
                messages.info(request, "Support ticket has been assigned.")
                return redirect("dashboard")

            # Check if the form for ticket resolution is submitted
            form_resolution = TicketResolutionForm(request.POST, instance=ticket)
            if form_resolution.is_valid():
                ticket = form_resolution.save(commit=False)
                status = form_resolution.cleaned_data.get("status")
                if status == "Resolved":
                    ticket.status = "Resolved"
                    ticket.resolved_by = request.user
                    
                    # Send the webhook message when the status changes to 'Resolved'
                    send_resolution_webhook(ticket.title, ticket.centre.name, request.user.username)
                
                ticket.save()
                
                messages.info(request, "Support ticket status has been updated.")
                return redirect("dashboard")

        else:
            # For other user roles, use the existing form
            form = SupportTicketUpdateForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                messages.info(request, "Ticket description has been updated.")
                return redirect("dashboard")
    else:
        if user_role == "technician_or_above":
            # Show both ticket resolution form and ticket assignment form to technicians
            form_resolution = TicketResolutionForm(instance=ticket)
            form_assignment = TicketAssignmentForm()
        else:
            # For other user roles, use the existing form
            form = SupportTicketUpdateForm(instance=ticket)

    technicians = User.objects.filter(role="technician")

    context = {
        "ticket": ticket,
        "user_role": user_role,
        "form_resolution": form_resolution,
        "form_assignment": form_assignment,
        "technicians": technicians,
    }

    return render(request, "support_ticket/ticket_details.html", context)



def send_assignment_webhook(ticket_title, ticket_centre, assigned_to):
    webhook_url = settings.WEB_HOOK_URL
    
    message = {
        'text': f'A Support Ticket *Title:* "{ticket_title}" at *{ticket_centre}* has been assigned to {assigned_to}.'
    }

    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    try:
        response = requests.post(
            url=webhook_url,
            headers=headers,
            data=json.dumps(message),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send webhook notification: {str(e)}")
       

def send_resolution_webhook(ticket_title, ticket_centre, resolved_by):
    webhook_url = settings.WEB_HOOK_URL
    
    message = {
        'text': f'Support Ticket *Title:* "{ticket_title}" at *{ticket_centre}* has been resolved by {resolved_by}.'
    }

    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    try:
        response = requests.post(
            url=webhook_url,
            headers=headers,
            data=json.dumps(message),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send webhook notification: {str(e)}")


@login_required
def create_ticket(request):
    if request.method == "POST":
        form = SupportTicketForm(request.POST, user=request.user)
        if form.is_valid():
            support_ticket = form.save(commit=False)
            support_ticket.submitted_by = request.user
            support_ticket.save()

            send_webhook_notification(support_ticket, request.user) 

            messages.success(request, "Support ticket created successfully.")
            return redirect("dashboard")
        else:
            form = SupportTicketForm(user=request.user)
            # Render the form with errors to display validation messages to the user
            context = {"form": form}
            return render(request, "support_ticket/create_ticket.html", context)
    else:
        form = SupportTicketForm(user=request.user)

    return render(request, "support_ticket/create_ticket.html", {"form": form})


def send_webhook_notification(support_ticket, user):
    webhook_url = settings.WEB_HOOK_URL
    app_message = {
        'text': f'A Support Ticket has been created at *{support_ticket.centre}*\n'
                f'*Title:* {support_ticket.title}\n'
                f'*Category:* {support_ticket.category}\n'
                f'*Subcategory:* {support_ticket.subcategory}\n'
                f'*Priority:* {support_ticket.priority}\n'
                f'*by:* {user}'
    }

    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    
    try:
        response = requests.post(
            url=webhook_url,
            headers=message_headers,
            data=json.dumps(app_message),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send webhook notification: {str(e)}")


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
    tickets = SupportTicket.objects.all()
    total_tickets_count = tickets.count()
    open_tickets_count = tickets.filter(status="Open").count()
    in_progress_tickets_count = tickets.filter(status="In Progress").count()
    resolved_tickets_count = tickets.filter(status="Resolved").count()

    if user.is_technician():
        # If the user is a technician, show tickets assigned to them
        tickets = tickets.filter(assigned_to=user)
    else:
        # If the user is not a technician, show their own submitted tickets
        tickets = tickets.filter(submitted_by=user)

    context = {
        "tickets": tickets,
        "total_tickets_count": total_tickets_count,
        "open_tickets_count": open_tickets_count,
        "in_progress_tickets_count": in_progress_tickets_count,
        "resolved_tickets_count": resolved_tickets_count,
    }

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
