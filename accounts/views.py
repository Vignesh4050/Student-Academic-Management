from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .forms import CreateUserForm

User = get_user_model()


@login_required
def dashboard(request):
    user = request.user
    if user.role == "ADMIN" or user.is_superuser:
        dashboard_name = "Administrator Dashboard"
    elif user.role == "FACULTY":
        dashboard_name = "Faculty Dashboard"
    else:
        dashboard_name = "Student Dashboard"

    context = {
        "dashboard_name": dashboard_name,
        "username": user.get_full_name() or user.username,
        "role": user.get_role_display(),
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def create_user(request):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        raise PermissionDenied("Only administrators can create user accounts.")

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User account created successfully.")
            return redirect("create_user")
    else:
        form = CreateUserForm()

    return render(request, "accounts/create_user.html", {"form": form})
