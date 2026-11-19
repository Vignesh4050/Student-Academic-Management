from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from academics.models import Student
from .models import Marks
from .forms import MarksForm


def get_marks_queryset(user):
    """
    Return only the marks records the user is allowed to access.
    """

    records = Marks.objects.select_related(
        "student",
        "subject",
        "subject__course",
        "subject__semester",
    )

    if user.role == "ADMIN":
        return records

    if user.role == "FACULTY":
        return records.filter(
            subject__faculty__user=user
        )

    if user.role == "STUDENT":
        try:
            student = user.student_profile
        except Student.DoesNotExist:
            return records.none()

        return records.filter(student=student)

    return records.none()


def can_manage_marks(user):
    return (
        user.is_authenticated
        and user.role in ["ADMIN", "FACULTY"]
    )


@login_required
def marks_list(request):
    records = get_marks_queryset(request.user).order_by(
        "student__roll_number",
        "subject__name",
    )

    return render(
        request,
        "marks/list.html",
        {"records": records},
    )


@login_required
def marks_create(request):
    if not can_manage_marks(request.user):
        raise PermissionDenied(
            "You are not permitted to enter marks."
        )

    if request.method == "POST":
        form = MarksForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Student marks saved successfully."
            )

            return redirect("marks_list")

    else:
        form = MarksForm(user=request.user)

    return render(
        request,
        "marks/form.html",
        {
            "form": form,
            "page_title": "Enter Student Marks",
        },
    )


@login_required
def marks_update(request, pk):
    if not can_manage_marks(request.user):
        raise PermissionDenied(
            "You are not permitted to update marks."
        )

    record = get_object_or_404(
        get_marks_queryset(request.user),
        pk=pk,
    )

    if request.method == "POST":
        form = MarksForm(
            request.POST,
            instance=record,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Student marks updated successfully."
            )

            return redirect("marks_list")

    else:
        form = MarksForm(
            instance=record,
            user=request.user,
        )

    return render(
        request,
        "marks/form.html",
        {
            "form": form,
            "page_title": "Update Student Marks",
        },
    )


@login_required
def marks_delete(request, pk):
    if not can_manage_marks(request.user):
        raise PermissionDenied(
            "You are not permitted to delete marks."
        )

    record = get_object_or_404(
        get_marks_queryset(request.user),
        pk=pk,
    )

    if request.method == "POST":
        record.delete()

        messages.success(
            request,
            "Marks record deleted successfully."
        )

        return redirect("marks_list")

    return render(
        request,
        "marks/confirm_delete.html",
        {"record": record},
    )