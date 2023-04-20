from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from techsupport.views import (
    CustomLoginView,
    HomeView,
    UserHomePageView,
    ManagerHomePageView,
    TechnicianHomePageView,
    AdminHomePageView,
    base,
    create_ticket,
    ticket_detail_user,
    ticket_detail_technician,
    manager_dashboard,
    admin_dashboard,
    ticket_list,
    update_ticket,
    edit_ticket,
    # KnowledgeBaseListView,
)

# Check user groups
user_groups = {
    "user": ["user"],
    "manager": ["manager"],
    "technician": ["technician"],
    "admin": ["admin"],
}

# Define decorator to check user groups
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(user):
        if user.is_authenticated:
            return bool(set(group_names) & set(user_groups.get(user.groups.first().name, [])))
        return False
    return user_passes_test(in_groups, login_url="/login/")

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    # path("custom-login-redirect/", views.custom_login_redirect, name="custom_login_redirect"),
    path("", HomeView.as_view(), name="home"),
    # path("", LoginView.as_view(), name="account_login"),
    path("", UserHomePageView.as_view(), name="home_user"),
    path("home/manager/", group_required("manager")(ManagerHomePageView.as_view()), name="home_manager"),
    path("home/technician/", group_required("technician")(TechnicianHomePageView.as_view()), name="home_technician"),
    path("home/admin/", group_required("admin")(AdminHomePageView.as_view()), name="home_admin"),
    path("base/", login_required(base), name="base"),
    path("create-ticket/", login_required(create_ticket), name="create_ticket"),
    path("ticket-detail/user/<int:pk>/", login_required(ticket_detail_user), name="ticket_detail_user"),
    path("ticket-detail/technician/<int:pk>/", login_required(ticket_detail_technician), name="ticket_detail_technician"),
    path("manager-dashboard/", group_required("manager")(manager_dashboard), name="manager_dashboard"),
    path("admin-dashboard/", group_required("admin")(admin_dashboard), name="admin_dashboard"),
    path("ticket-list/", login_required(ticket_list), name="ticket_list"),
    path("update-ticket/<int:pk>/", login_required(update_ticket), name="update_ticket"),
    path("edit-ticket/<int:pk>/", group_required("technician")(edit_ticket), name="edit_ticket"),
    # path("knowledge-base/", KnowledgeBaseListView.as_view(), name="knowledge_base_list"),
]
