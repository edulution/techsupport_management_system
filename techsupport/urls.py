from django.urls import path, include
from . import views

# URL routing for various pages of the tech support management system.

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/base/", views.base, name="base"),
    path("accounts/login/", views.CustomLoginView.as_view(), name="account_login"),
    path("support_ticket/create/", views.create_ticket, name="create_ticket"),
    path("support_ticket/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path("support_ticket/<int:pk>/update/", views.update_ticket, name="update_ticket"),
    path("support_ticket/", views.ticket_list, name="ticket_list"),
    path("support_ticket/<int:ticket_id>/edit/", views.edit_ticket, name="edit_ticket"),
    path("support_ticket/admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("support_ticket/coach_ticket_detail/<int:pk>/", views.CoachTicketDetailView.as_view(), name="coach_ticket_detail"),
    path("support_ticket/manager_dashboard/", views.manager_dashboard, name="manager_dashboard"),
    path("support_ticket/coach_ticket_list/", views.CoachTicketListView.as_view(), name="coach_ticket_list"),
]
