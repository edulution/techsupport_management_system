from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .views import (
    UserHomePageView,
    ManagerHomePageView,
    TechnicianHomePageView,
    AdminHomePageView,
    CustomLoginView,
    profile,
    base,
    create_ticket,
    ticket_detail_user,
    ticket_detail_technician,
    manager_dashboard,
    admin_dashboard,
    ticket_list,
    update_ticket,
    edit_ticket,
    KnowledgeBaseListView,
)

urlpatterns = [
    path("", LoginView.as_view(), name="account_login"),
    path("home/user/", UserHomePageView.as_view(), name="home_user"),
    path("home/manager/", ManagerHomePageView.as_view(), name="home_manager"),
    path("home/technician/", TechnicianHomePageView.as_view(), name="home_technician"),
    path("home/admin/", AdminHomePageView.as_view(), name="home_admin"),
    path("login/", CustomLoginView.as_view(), name="account_login"),
    path("profile/", profile, name="profile"),
    path("base/", base, name="base"),
    path("create-ticket/", create_ticket, name="create_ticket"),
    path("ticket/<int:ticket_id>/", ticket_detail_user, name="ticket_detail"),
    path("ticket/<int:ticket_id>/technician/", ticket_detail_technician, name="ticket_detail_technician"),
    path("manager-dashboard/", manager_dashboard, name="manager_dashboard"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("ticket-list/", ticket_list, name="ticket_list"),
    path("update-ticket/<int:ticket_id>/", update_ticket, name="update_ticket"),
    path("edit-ticket/<int:ticket_id>/", edit_ticket, name="edit_ticket"),
    path("knowledge_base/", KnowledgeBaseListView.as_view(), name="knowledge_base"),
]
