from django.urls import path
from .views import (
    user_login,
    user_logout,
    dashboard,
    profile,
    ticket_details,
    create_ticket,
    all_tickets,
    ticket_queue,
    close_ticket,
    all_closed_tickets,
    settings_view,
    assign_ticket,
    open_tickets,
    resolved_tickets,
    tickets_in_progress,
    get_subcategories,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("", dashboard, name="dashboard"),
    path("profile/", profile, name="profile"),
    path('ticket_details/<uuid:ticket_id>/', ticket_details, name='ticket_details'),
    path("create_ticket/", create_ticket, name="create_ticket"),
    path("all_tickets/", all_tickets, name="all_tickets"),
    path("ticket_queue/", ticket_queue, name="ticket_queue"),
    path("close_ticket/", close_ticket, name="close_ticket"),
    path("all_closed_tickets/", all_closed_tickets, name="all_closed_tickets"),
    path("settings/", settings_view, name="settings"),
    path('assign_ticket/', assign_ticket, name="assign_ticket"),
    path('open_tickets/', open_tickets, name='open_tickets'),
    path('resolved_tickets/', resolved_tickets, name='resolved_tickets'),
    path('tickets_in_progress/', tickets_in_progress, name='tickets_in_progress'),
    path('get_subcategories/', get_subcategories, name='get_subcategories'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
