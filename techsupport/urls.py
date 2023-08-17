from django.urls import path
from .views import (
    user_login,
    user_logout,
    dashboard,
    profile,
    ticket_details,
    create_ticket,
    all_tickets,
    settings_view,
    assign_ticket,
    open_tickets,
    resolved_tickets,
    tickets_in_progress,
    get_subcategories,
    export_tickets_csv,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("", dashboard, name="dashboard"),
    path("profile/", profile, name="profile"),
    path("profile/logout/", user_logout, name="logout"),
    path('ticket_details/<uuid:ticket_id>/', ticket_details, name='ticket_details'),
    path("create_ticket/", create_ticket, name="create_ticket"),
    path("export_tickets_csv/", export_tickets_csv, name="export_tickets_csv"),
    path("create_ticket/logout/", user_logout, name="logout"),
    path("all_tickets/", all_tickets, name="all_tickets"),
    path("all_tickets/logout/", user_logout, name="logout"),
    path("settings/", settings_view, name="settings"),
    path("settings/logout/", user_logout, name="logout"),
    path('assign_ticket/', assign_ticket, name="assign_ticket"),
    path('assign_ticket/logout/', user_logout, name="logout"),
    path('open_tickets/', open_tickets, name='open_tickets'),
    path('resolved_tickets/', resolved_tickets, name='resolved_tickets'),
    path('tickets_in_progress/', tickets_in_progress, name='tickets_in_progress'),
    path('get_subcategories/', get_subcategories, name='get_subcategories'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
