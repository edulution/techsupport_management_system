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
    profile_api,
    ticket_details_api,
    create_ticket_api,
    all_tickets_api,
    open_tickets_api,
    resolved_tickets_api,
    tickets_in_progress_api,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/create_ticket/', create_ticket_api, name='create-ticket-api'),
    path('api/tickets/<int:ticket_id>/', ticket_details_api, name='ticket-details-api'),
    path('api/profile/', profile_api, name='profile-api'),
    path('api/all_tickets/', all_tickets_api, name='all-tickets-api'),
    path('api/open_tickets/', open_tickets_api, name='open-tickets-api'),
    path('api/resolved_tickets/', resolved_tickets_api, name='resolved-tickets-api'),
    path('api/tickets_in_progress/', tickets_in_progress_api, name='tickets-in-progress-api'),
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
