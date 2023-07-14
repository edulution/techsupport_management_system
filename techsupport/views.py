from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import SupportTicketForm, UserTicketUpdateForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket, UserProfile , User
# from django.contrib.auth.models import User




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


#     return render(request, "dashboard.html", context)
@login_required
def dashboard(request):
    # Fetch and filter the tickets based on your requirements
    tickets = SupportTicket.objects.filter(submitted_by=request.user).order_by('-date_submitted')

    # Calculate ticket counts for each status
    open_tickets_count = tickets.filter(status='open').count()
    in_progress_tickets_count = tickets.filter(status='in_progress').count()
    resolved_tickets_count = tickets.filter(status='resolved').count()

    context = {
        'tickets': tickets,
        'open_tickets_count': open_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'resolved_tickets_count': resolved_tickets_count,
        'search_query': request.GET.get('search_query', ''),
    }

    return render(request, 'dashboard.html', context)


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
def ticket_details(request, ticket_id):
    """ view ticket details view function to view ticket details and return a rendered response using the 'view_ticket_details.html' template """  
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    ticket = SupportTicket.objects.get(id=ticket_id)
    context = {'ticket': ticket}
    return render(request, 'support_ticket/ticket_details.html', context)


# @login_required
# def create_ticket(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     if request.method == "POST":
#         form = SupportTicketForm(request.POST, user=request.user)
#         if form.is_valid():
#             var = form
#             var.submitted_by = request.user
#             var.status = "open"
#             var.save()     

#             # # var.ticket_number = SupportTicket.id.hex[:5]
#             # var.title = SupportTicket.title
#             # var.priority = SupportTicket.priority
#             # # var.ticket_age = timezone.now() - SupportTicket.date_submitted
#             # var.save()

#             messages.info(request, "Ticket created successfully. Please wait for a technician to respond.")
#             return redirect('dashboard')
#         else:
#             messages.warning(request, "Ticket creation failed")
#             return redirect('dashboard')    
#     else:
#         form = SupportTicketForm(user=request.user)
#         context = {'form': form}
#         return render(request, 'support_ticket/create_ticket.html', context)
# views.py
@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, user=request.user)
        if form.is_valid():
            support_ticket = form.save(commit=False)
            support_ticket.submitted_by = request.user
            support_ticket.status = SupportTicket.Status.OPEN
            support_ticket.save()
            messages.success(request, 'Support ticket created successfully.')
            return redirect('dashboard')
    else:
        form = SupportTicketForm(user=request.user)
    
    context = {'form': form,
               'user_submit': User.objects.filter(username=request.user)
               }
    return render(request, 'support_ticket/create_ticket.html', context)




@login_required
def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})




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
