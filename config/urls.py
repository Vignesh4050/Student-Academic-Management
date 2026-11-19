from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

from accounts import views as account_views
from reports.views import DashboardView


urlpatterns = [
    path("admin/", admin.site.urls),

    # Keep the global dashboard name for LOGIN_REDIRECT_URL and existing links.
    path("", DashboardView.as_view(), name="dashboard"),

    # Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),

    # Namespaced Reports URLs (dashboard and performance reports).
    path(
        "",
        include(("reports.urls", "reports"), namespace="reports"),
    ),

    # Account management (kept un-namespaced; URL names are global).
    path("home/", account_views.dashboard, name="home_dashboard"),
    path("accounts/", include("accounts.urls")),

    # Namespaced academic management URLs.
    path(
        "academics/",
        include(("academics.urls", "academics"), namespace="academics"),
    ),

    # Attendance and marks URLs remain global, matching their current views.
    path("attendance/", include("attendance.urls")),
    path("marks/", include("marks.urls")),
]
