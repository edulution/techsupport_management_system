from django.core.paginator import Paginator
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
from django.db.models import Q, Avg
from django.views.generic import ListView
from django.views import View
from django.urls import reverse_lazy
from django import forms


from .forms import TicketCreateForm, SupportTicketForm, TicketUpdateForm
from .models import Country, Region, Centre, Category, SubCategory, SupportTicket


# Login view


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


@login_required
def profile(request):
    return render(request, "registration/profile.html")


def base(request):
    return render(request, "registration/base.html")


class HomeView(TemplateView):
    template_name = "home.html"


# user"s home page that inherits from the TemplateView class and adds the list of support tickets related to the logged-in user to the context data of the template.


class UserHomePageView(LoginRequiredMixin, View):
    template_name = "home_user.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Ticket successfully created.")
            return redirect("home_user")

        context = self.get_context_data(**kwargs)
        context["form"] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {}
        context["tickets"] = SupportTicket.objects.filter(user=self.request.user)
        context["form"] = SupportTicketForm()
        # context["knowledge_base"] = KnowledgeBase.objects.all()
        return context


# KnowledgeBaseListView
# class KnowledgeBaseListView(ListView):
#     model = KnowledgeBase
#     template_name = "knowledge_base.html"
#     context_object_name = "knowledge_base_list"


# contains all the support tickets that are assigned to the manager's region.


class ManagerHomePageView(LoginRequiredMixin, ListView):
    template_name = "home_manager.html"
    model = SupportTicket
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(region=self.request.user.region)

        # Sorting
        sort_by = self.request.GET.get("sort_by")
        if sort_by:
            if sort_by == "date":
                queryset = queryset.order_by("-date")
            elif sort_by == "priority":
                queryset = queryset.order_by("priority")
            elif sort_by == "status":
                queryset = queryset.order_by("status")

        # Searching
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(ticket_number__icontains=search_query)
                | Q(user_name__icontains=search_query)
            )

        # Filtering
        filter_by = self.request.GET.get("filter_by")
        if filter_by:
            if filter_by == "open":
                queryset = queryset.filter(status="Open")
            elif filter_by == "closed":
                queryset = queryset.filter(status="Closed")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pagination
        paginator = Paginator(context["object_list"], self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj

        # Additional features
        context["search_query"] = self.request.GET.get("q")
        context["sort_by"] = self.request.GET.get("sort_by")
        context["filter_by"] = self.request.GET.get("filter_by")
        context["ticket_details_url"] = "ticket_details"

        return context


# This view for the technician homepage that retrieves and renders a list of support tickets assigned to the current logged-in technician.


class TechnicianHomePageView(LoginRequiredMixin, TemplateView):
    template_name = "home_technician.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tickets = SupportTicket.objects.filter(technician=self.request.user)

        # Pagination
        page_number = self.request.GET.get("page")
        paginator = Paginator(tickets, 10)  # Show 10 tickets per page
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj

        # Sorting
        sort_by = self.request.GET.get("sort_by")
        if sort_by == "date":
            tickets = tickets.order_by("-created_at")
        elif sort_by == "priority":
            tickets = tickets.order_by("priority")
        elif sort_by == "status":
            tickets = tickets.order_by("status")
        context["sort_by"] = sort_by

        # Search
        search_query = self.request.GET.get("q")
        if search_query:
            tickets = tickets.filter(
                Q(ticket_number__icontains=search_query)
                | Q(user__name__icontains=search_query)
            )
        context["search_query"] = search_query

        # Filtering
        priority_filter = self.request.GET.get("priority")
        status_filter = self.request.GET.get("status")
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter)
        if status_filter:
            tickets = tickets.filter(status=status_filter)
        context["priority_filter"] = priority_filter
        context["status_filter"] = status_filter

        # Ticket details
        context["ticket_details_url"] = reverse_lazy("ticket_details")

        # Notifications
        new_tickets_count = SupportTicket.objects.filter(
            technician=self.request.user, status="new"
        ).count()
        context["new_tickets_count"] = new_tickets_count

        # Technician availability
        context["technician_availability"] = self.request.user.is_available

        # Ticket history
        context["ticket_history_url"] = reverse_lazy("ticket_history")

        context["tickets"] = tickets
        return context


# This view adds a "tickets" key to the context dictionary, which contains all SupportTicket objects, and renders the "home_admin.html" template.


class AdminHomePageView(LoginRequiredMixin, TemplateView):
    template_name = "home_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Feature 1: Dashboard summary
        open_tickets_count = SupportTicket.objects.filter(status="Open").count()
        closed_tickets_count = SupportTicket.objects.filter(status="Closed").count()
        avg_response_time = SupportTicket.objects.filter(status="Closed").aggregate(
            avg_response_time=Avg("response_time")
        )
        ticket_categories = Category.objects.all()
        context["dashboard_summary"] = {
            "open_tickets_count": open_tickets_count,
            "closed_tickets_count": closed_tickets_count,
            "avg_response_time": avg_response_time,
            "ticket_categories": ticket_categories,
        }
        # Feature 2: List of recent/high-priority tickets
        recent_tickets = SupportTicket.objects.order_by("-created_at")[:10]
        high_priority_tickets = SupportTicket.objects.filter(
            priority__in=["High", "Urgent"]
        )
        context["recent_tickets"] = recent_tickets
        context["high_priority_tickets"] = high_priority_tickets
        # Feature 3: Search bar
        search_query = self.request.GET.get("search_query")
        if search_query:
            tickets = SupportTicket.objects.filter(
                Q(title__icontains=search_query)
                | Q(user__email__icontains=search_query)
            )
        else:
            tickets = SupportTicket.objects.all()
        context["tickets"] = tickets
        # Feature 4: Button to admin dashboard
        context["admin_dashboard_url"] = "/admin/"
        # Feature 5: Technicians working on tickets
        technicians = User.objects.filter(groups__name="Technicians")
        technician_tickets = {}
        for technician in technicians:
            technician_tickets[technician.username] = SupportTicket.objects.filter(
                technician=technician, status="In Progress"
            )
        context["technician_tickets"] = technician_tickets
        # Feature 6: Notification center
        new_tickets_count = SupportTicket.objects.filter(status="New").count()
        context["new_tickets_count"] = new_tickets_count
        # Feature 7: Navigation bar
        context["settings_url"] = "/admin/settings/"
        context["reports_url"] = "/admin/reports/"
        context["user_management_url"] = "/admin/users/"
        return context


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
            return redirect("ticket_detail_user", ticket_id=ticket.id)
        else:
            messages.error(request, "There was an error creating your ticket.")
    else:
        form = TicketCreateForm()
    return render(request, "support_ticket/create_ticket.html", {"form": form})


# Support ticket detail view for user/coach


@login_required(login_url="account_login")
def ticket_detail_user(request, ticket_id):
    # Get the support ticket object with the given ticket_id or return a 404 error if not found
    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    # Check if the user/coach has permission to view the ticket
    if request.user == ticket.user:
        return render(
            request, "support_ticket/ticket_detail_user.html", {"ticket": ticket}
        )
    else:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect("home_user")


# Technician ticket detail view


@login_required(login_url="account_login")
def ticket_detail_technician(request, ticket_id):
    # Get the support ticket object with the given ticket_id or return a 404 error if not found
    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    # Check if the technician has permission to view the ticket
    if request.user == ticket.technician:
        return render(
            request, "support_ticket/ticket_detail_technician.html", {"ticket": ticket}
        )
    else:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect("home_technician")


# A function to check if the coach belongs to the manager group


def is_manager(user):
    return user.is_authenticated and user.is_manager


# A view that displays the dashboard for managers only
# It gets all support tickets that belong to the manager"s assigned region/cluster and passes them to the template


@user_passes_test(is_manager)
def manager_dashboard(request):
    manager = request.user.manager_profile
    tickets = SupportTicket.objects.filter(cluster=manager.cluster)
    return render(
        request, "support_ticket/manager_dashboard.html", {"tickets": tickets}
    )


# Edit support ticket view for technician and admin
@login_required(login_url="account_login")
def edit_ticket(request, ticket_id):
    # Retrieve the ticket object with the given ID
    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    if request.method == "GET":
        # Render the ticket form with the existing ticket data
        return render(
            request,
            "support_ticket/edit_ticket.html",
            {"form": TicketCreateForm(instance=ticket)},
        )

    # If this is a POST request, validate the submitted form data and update the ticket
    form = TicketCreateForm(request.POST, instance=ticket)
    if form.is_valid():
        ticket.updated_at = timezone.now()
        ticket.save()
        return redirect("ticket_detail", ticket_id=ticket.id)

    # If the form data is invalid, re-render the form with the error messages
    return render(request, "support_ticket/edit_ticket.html", {"form": form})


# Update a support ticket


@login_required(login_url="account_login")
def update_ticket(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)

    # Check if the user/coach is authorized to update the ticket
    if (
        request.user.groups.filter(name="technician").exists()
        or request.user.is_superuser
    ):
        # If it is a POST request, update the ticket with the new data
        if request.method == "POST":
            if TicketUpdateForm(request.POST, instance=ticket).is_valid():
                ticket.save()
                messages.success(request, "Ticket updated successfully!")
                return redirect("ticket_detail", pk=pk)
        else:
            # If it is a GET request, display the ticket update form
            form = TicketUpdateForm(instance=ticket)
            return render(
                request,
                "support_ticket/update_ticket.html",
                {"form": form, "ticket": ticket},
            )
    else:
        messages.error(request, "You are not authorized to update this ticket.")
        return redirect("home")


# Support ticket list view for technician and admin


@login_required(login_url="account_login")
@user_passes_test(
    lambda user: user.groups.filter(name="technician").exists() or user.is_superuser
)
def ticket_list(request):
    tickets = SupportTicket.objects.all()
    return render(request, "support_ticket/ticket_list.html", {"tickets": tickets})


# Support ticket detail view for technician and superuser


@login_required(login_url="account_login")
def ticket_detail(request, ticket_id):
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        raise Http404("Ticket does not exist")

    # check if user is authorized to view this ticket
    if not (
        request.user.groups.filter(name="technician").exists()
        or request.user.is_superuser
        or request.user == ticket.user
    ):
        messages.error(request, "You are not authorized to view this ticket")
        return redirect("ticket_list")

    if request.method == "POST":
        if TicketUpdateForm(request.POST, instance=ticket).is_valid():
            TicketUpdateForm(request.POST, instance=ticket).save()
            messages.success(request, "Ticket has been updated")
            return redirect("ticket_detail", ticket_id=ticket.id)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(
        request, "support_ticket/ticket_detail.html", {"ticket": ticket, "form": form}
    )


# Support ticket list view for field coordinators/managers and admin
@login_required(login_url="account_login")
def coach_ticket_list(request):
    if request.user.groups.filter(name="manager").exists() or request.user.is_superuser:
        tickets = SupportTicket.objects.all()
    else:
        tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, "support_ticket/ticket_list.html", {"tickets": tickets})


# Admin dashboard view


@login_required(login_url="account_login")
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    user = request.user
    total_tickets = SupportTicket.objects.count()
    open_tickets = SupportTicket.objects.filter(status="Open").count()
    closed_tickets = SupportTicket.objects.filter(status="Closed").count()
    tech_users = User.objects.filter(groups__name="technician").count()
    return render(
        request,
        "support_ticket/admin_dashboard.html",
        {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "closed_tickets": closed_tickets,
            "tech_users": tech_users,
        },
    )
