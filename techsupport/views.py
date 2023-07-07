from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import SupportTicketForm, UserTicketUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket, UserProfile



def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error_message = "Invalid username or password"
    else:
        error_message = None
    return render(request, "accounts/login.html", {"error_message": error_message})


def user_logout(request):
    logout(request)
    return render(request, "accounts/login.html")


@login_required
def dashboard(request):
    """Renders the dashboard view with dynamic content based on user roles and returns a rendered response using the 'dashboard.html' template"""
    search_query = request.GET.get("search_query", "")
    user = request.user
    role = user.role if user.is_authenticated else None
    tickets = SupportTicket.objects.filter(submitted_by=user)
    technician_or_above = role in ["technician", "admin", "super_admin"]
    all_users = role in ["user", "manager", "technician", "admin", "super_admin"]
    admin_or_above = role in ["admin", "super_admin"]

    context = {
        "role": role,
        "technician_or_above": technician_or_above,
        "all_users": all_users,
        "admin_or_above": admin_or_above,
        "tickets": tickets,
        "search_query": search_query,
    }

    return render(request, "dashboard.html", context)

@login_required
def profile(request):
    details = UserProfile.objects.filter(user=request.user.pk)
    user = request.user
    try:
        profile = user.profile 
    except UserProfile.DoesNotExist:
        profile = None
    
    context = {
        'profile': profile,
        'details': details,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def ticket_details(request, pk):
    """ view ticket details view function to view ticket details and return a rendered response using the 'view_ticket_details.html' template """  
    
    ticket = SupportTicket.objects.get(pk=pk)
    context = {'ticket': ticket}
    return render(request, 'support_ticket/ticket_details.html', context)


# @login_required
# def create_ticket(request):
#     """ create_ticket view function to create a new ticket and return a rendered response using the 'create_ticket.html' template """

#     if request.method == "POST":
#         form = SupportTicketForm(request.POST)
#         if form.is_valid():
#             support_ticket = form.save(commit=False)
#             support_ticket.created_by = request.user
#             support_ticket.ticket_status = "open"
#             support_ticket.save()

#             messages.info(request, "Ticket created successfully. Please wait for a technician to respond.")
#             return redirect('dashboard')  # Replace 'dashboard' with your actual URL name for the dashboard
#         else:
#             messages.warning(request, "Ticket creation failed")
#             return redirect('create_ticket')  # Replace 'create_ticket' with your actual URL name for the create ticket page
#     else:
#         form = SupportTicketForm()
#         context = {'form': form}
#         return render(request, 'support_ticket/create_ticket.html', context)
@login_required
def create_ticket(request):
    if request.method == "POST":
        form = SupportTicketForm(request.POST, user=request.user)  # Pass the user parameter
        if form.is_valid():
            support_ticket = form.save(commit=False)
            support_ticket.created_by = request.user
            support_ticket.ticket_status = "open"
            support_ticket.save()

            messages.info(request, "Ticket created successfully. Please wait for a technician to respond.")
            return redirect('dashboard')
        else:
            messages.warning(request, "Ticket creation failed")
            return redirect('create_ticket')
    else:
        form = SupportTicketForm(user=request.user)  # Pass the user parameter
        context = {'form': form}
        return render(request, 'support_ticket/create_ticket.html', context)




@login_required
def update_ticket(request, pk):
    """update_ticket view function to update a ticket and return a rendered response using the 'update_ticket.html' template"""
    ticket = SupportTicket.objects.get(pk=pk)
    form = UserTicketUpdateForm(instance=ticket)

    if request.user.role not in ["technician", "admin", "super_admin"]:
        messages.warning(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    if request.method == "POST":
        form = SupportTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.info(request, "Ticket has been updated successfully")
            return redirect('dashboard')
        else:
            messages.warning(request, "Ticket update failed")

    context = {'form': form}
    return render(request, 'support_ticket/update_ticket.html', context)

    

@login_required
def all_tickets(request):
    """ view_all_tickets view function to view all tickets and return a rendered response using the 'view_all_tickets.html' template """    
    
    tickets = SupportTicket.objects.all()
    context = {'tickets': tickets}
    return render(request, 'support_ticket/all_tickets.html', context)


@login_required
def ticket_queue(request):
    """ ticket_query view function to query a ticket and return a rendered response using the 'ticket_query.html' template """  
    
    tickets = SupportTicket.objects.filter(ticket_status="open")
    context = {'tickets': tickets} 
    return render(request, 'support_ticket/ticket_queue.html', context)



@login_required
def take_ticket(request, pk):
    """ take_ticket view function to take a ticket and return a rendered response using the 'take_ticket.html' template """ 
    
    ticket = SupportTicket.objects.get(pk=pk)
    ticket.assigned_to = request.user
    ticket.ticket_status = "in_progress"
    ticket.save()
    messages.info(request, "Ticket has been assigned to you")
    return redirect('take_ticket')

  
@login_required
def close_ticket(request, pk):
    """close_ticket view function to close a ticket and return a rendered response using the 'close_ticket.html' template """ 
    
    ticket = SupportTicket.objects.get(pk=pk)
    ticket.ticket_status = "closed"
    ticket.is_resolved = True
    ticket.closed_date = timezone.now()
    ticket.save()
    messages.info(request, "Ticket has been closed by Technician")
    return redirect('support_ticket/ticket_que.html')

 
@login_required
def workspace(request):
    """ Technician_active_tickets view function to view all active tickets and return a rendered response using the 'Technician_active_tickets.html' template """  
    
    tickets = SupportTicket.objects.filter(assigned_to=request.user, is_resolved=False)
    context = {'tickets': tickets}
    return render(request, 'support_ticket/workspace.html', context)


@login_required
def all_closed_tickets(request):
    """ all closed/resolved tickets view function to view all closed tickets and return a rendered response using the 'all_closed_tickets.html' template """    
    
    tickets = SupportTicket.objects.filter(assignee=request.user, is_resolved=True)
    context = {'tickets': tickets}
    return render(request, 'support_ticket/all_closed_tickets.html', context)


@login_required
def settings_view(request):
    """ settings view """

    user = request.user
    dark_mode_enabled = user.dark_mode_enabled
    
    if request.method == 'POST':
        dark_mode_enabled = request.POST.get('dark_mode_enabled') == 'on'
        user.dark_mode_enabled = dark_mode_enabled
        user.save()
        return redirect('settings')
    
    context = {
        'dark_mode_enabled': dark_mode_enabled,
    }
    return render(request, 'support_ticket/settings.html', context)


def mark_ticket_resolved(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        ticket = SupportTicket.objects.get(id=ticket_id)
        ticket.status = SupportTicket.Status.RESOLVED
        ticket.save()
    return redirect('dashboard')


def toggle_dark_mode(request):
    user = request.user
    if request.method == 'POST':
        dark_mode_enabled = request.POST.get('dark_mode_enabled') == 'on'
        user.dark_mode_enabled = dark_mode_enabled
        user.save()
    return redirect('dashboard')


def assign_ticket(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        technician_id = request.POST.get('technician_id')
        ticket = SupportTicket.objects.get(id=ticket_id)
        technician = User.objects.get(id=technician_id)
        ticket.resolved_by = technician
        ticket.save()
        return redirect('dashboard')
    else:
        # Handle GET request if needed
        pass

def open_tickets(request):
    # Retrieve open tickets from the database
    tickets = SupportTicket.objects.filter(status='Open')
    context = {'tickets': tickets}
    return render(request, 'support_ticket/open_tickets.html', context)

def resolved_tickets(request):
    # Retrieve resolved tickets from the database
    tickets = SupportTicket.objects.filter(status='Resolved')
    context = {'tickets': tickets}
    return render(request, 'support_ticket/resolved_tickets.html', context)

def tickets_in_progress(request):
    tickets = SupportTicket.objects.filter(status='In Progress')
    return render(request, 'support_ticket/tickets_in_progress.html', {'tickets': tickets})