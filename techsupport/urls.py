from django.urls import path
from .views import (
    user_login,
    user_logout,
    dashboard,
    profile,
    ticket_details,
    create_ticket,
    all_tickets,
    # settings_view,
    assign_ticket,
    open_tickets,
    resolved_tickets,
    tickets_in_progress,
    get_subcategories,
    export_tickets_csv,
)
from .api import (
    CreateTicketAPIView,
    TicketDetailsAPIView,
    ProfileAPIView,
    AllTicketsAPIView,
    OpenTicketsAPIView,
    ResolvedTicketsAPIView,
    TicketsInProgressAPIView,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/create_ticket/', CreateTicketAPIView.as_view(), name='create-ticket-api'),
    path('api/ticket_details/<int:ticket_id>/', TicketDetailsAPIView.as_view(), name='ticket-details-api'),
    path('api/profile/', ProfileAPIView.as_view(), name='profile-api'),
    path('api/all_tickets/', AllTicketsAPIView.as_view(), name='all-tickets-api'),
    path('api/open_tickets/', OpenTicketsAPIView.as_view(), name='open-tickets-api'),
    path('api/resolved_tickets/', ResolvedTicketsAPIView.as_view(), name='resolved-tickets-api'),
    path('api/tickets_in_progress/', TicketsInProgressAPIView.as_view(), name='tickets-in-progress-api'),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("", dashboard, name="dashboard"),
    path("profile/", profile, name="profile"),
    path("ticket_details/<uuid:ticket_id>/", ticket_details, name="ticket_details"),
    path("create_ticket/", create_ticket, name="create_ticket"),
    path("export_tickets_csv/", export_tickets_csv, name="export_tickets_csv"),
    path("all_tickets/", all_tickets, name="all_tickets"),
    # path("settings/", settings_view, name="settings"),
    path("assign_ticket/", assign_ticket, name="assign_ticket"),
    path("open_tickets/", open_tickets, name="open_tickets"),
    path("resolved_tickets/", resolved_tickets, name="resolved_tickets"),
    path("tickets_in_progress/", tickets_in_progress, name="tickets_in_progress"),
    path("get_subcategories/", get_subcategories, name="get_subcategories"),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
