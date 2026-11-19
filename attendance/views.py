from datetime import date as date_type

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date

from academics.models import Subject, Student
from .models import Attendance
from .forms import AttendanceSessionForm, AttendanceEntryFormSet


ATTENDANCE_THRESHOLD = 75


def get_authorized_subjects(user):
    """
    Administrators can manage all subjects.
    Faculty members can manage only their assigned subjects.
    """

    subjects = Subject.objects.select_related(
        "course",
        "semester",
        "faculty",
    )

    if user.role == "ADMIN":
        return subjects

    if user.role == "FACULTY":
        try:
            faculty_profile = user.faculty_profile
        except Exception:
            return Subject.objects.none()

        return subjects.filter(faculty=faculty_profile)

    return Subject.objects.none()


def get_enrolled_students(subject):
    """
    Return students enrolled in the selected course and semester.
    """

    return Student.objects.filter(
        course=subject.course,
        semester=subject.semester,
    ).order_by("roll_number")


def parse_attendance_date(value):
    """
    Accept only valid dates that are not in the future.
    """

    parsed = parse_date(value) if value else None

    if parsed is None:
        return None

    if parsed > date_type.today():
        return None

    return parsed


@login_required
def mark_attendance(request):
    """
    Display the attendance form and save attendance records.
    """

    if request.user.role not in ["ADMIN", "FACULTY"]:
        raise PermissionDenied(
            "Only administrators and faculty can record attendance."
        )

    authorized_subjects = get_authorized_subjects(request.user)

    if request.method == "POST":
        subject_id = request.POST.get("subject_id")

        selected_date = parse_attendance_date(
            request.POST.get("attendance_date")
        )

        subject = authorized_subjects.filter(
            pk=subject_id
        ).first()

        if subject is None:
            raise PermissionDenied(
                "You are not authorized to manage this subject."
            )

        if selected_date is None:
            messages.error(
                request,
                "Please select a valid date that is not in the future."
            )
            return redirect("mark_attendance")

        students = list(get_enrolled_students(subject))

        formset = AttendanceEntryFormSet(request.POST)

        # Prepare student/form pairs for the template.
        attendance_rows = list(zip(students, formset.forms))

        if not formset.is_valid():
            messages.error(
                request,
                "Some attendance entries are invalid."
            )

            return render(
                request,
                "attendance/mark_attendance.html",
                {
                    "session_form": AttendanceSessionForm(
                        initial={
                            "subject": subject,
                            "date": selected_date,
                        }
                    ),
                    "formset": formset,
                    "selected_subject": subject,
                    "selected_date": selected_date,
                    "students": students,
                    "attendance_rows": attendance_rows,
                    "show_attendance_form": True,
                },
            )

        submitted_ids = [
            form.cleaned_data["student_id"]
            for form in formset.forms
        ]

        expected_ids = [student.pk for student in students]

        # Do not accept missing, duplicated, or unrelated student IDs.
        if (
            len(submitted_ids) != len(set(submitted_ids))
            or set(submitted_ids) != set(expected_ids)
        ):
            messages.error(
                request,
                "The student list has changed or contains invalid entries. "
                "Please reload the attendance page."
            )
            return redirect("mark_attendance")

        with transaction.atomic():
            for form in formset.forms:
                student_id = form.cleaned_data["student_id"]
                status = form.cleaned_data["status"]

                Attendance.objects.update_or_create(
                    student_id=student_id,
                    subject=subject,
                    date=selected_date,
                    defaults={"status": status},
                )

        messages.success(
            request,
            "Attendance saved successfully."
        )

        return redirect(
            f"/attendance/mark/?subject={subject.pk}"
            f"&date={selected_date.isoformat()}"
        )

    # GET request: display the subject/date selection form.
    session_form = AttendanceSessionForm(
        initial={"date": date_type.today()}
    )

    selected_subject = None
    selected_date = None
    students = []
    formset = None
    attendance_rows = []

    subject_id = request.GET.get("subject")
    date_value = request.GET.get("date")

    if subject_id and date_value:
        selected_subject = authorized_subjects.filter(
            pk=subject_id
        ).first()

        selected_date = parse_attendance_date(date_value)

        if selected_subject is None:
            raise PermissionDenied(
                "You are not authorized to access this subject."
            )

        if selected_date is None:
            messages.error(
                request,
                "Please select a valid attendance date."
            )
        else:
            students = list(
                get_enrolled_students(selected_subject)
            )

            existing_records = {
                record.student_id: record.status
                for record in Attendance.objects.filter(
                    subject=selected_subject,
                    date=selected_date,
                    student__in=students,
                )
            }

            initial_data = [
                {
                    "student_id": student.pk,
                    "status": existing_records.get(
                        student.pk,
                        "PRESENT",
                    ),
                }
                for student in students
            ]

            formset = AttendanceEntryFormSet(
                initial=initial_data
            )

            attendance_rows = list(
                zip(students, formset.forms)
            )

    return render(
        request,
        "attendance/mark_attendance.html",
        {
            "session_form": session_form,
            "formset": formset,
            "selected_subject": selected_subject,
            "selected_date": selected_date,
            "students": students,
            "attendance_rows": attendance_rows,
            "show_attendance_form": formset is not None,
        },
    )


@login_required
def attendance_history(request):
    """
    Display attendance records permitted for the current user.
    """

    if request.user.role == "ADMIN":
        records = Attendance.objects.all()

    elif request.user.role == "FACULTY":
        records = Attendance.objects.filter(
            subject__faculty__user=request.user
        )

    elif request.user.role == "STUDENT":
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            student = None

        if student is None:
            records = Attendance.objects.none()
        else:
            records = Attendance.objects.filter(
                student=student
            )

    else:
        raise PermissionDenied

    records = records.select_related(
        "student",
        "subject",
    ).order_by(
        "-date",
        "subject__name",
        "student__roll_number",
    )

    return render(
        request,
        "attendance/history.html",
        {"records": records},
    )


@login_required
def attendance_summary(request):
    """
    Calculate attendance percentages for the current user.
    """

    if request.user.role == "STUDENT":
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            student = None

        students = (
            Student.objects.filter(pk=student.pk)
            if student
            else Student.objects.none()
        )

    elif request.user.role in ["ADMIN", "FACULTY"]:
        subjects = get_authorized_subjects(request.user)

        students = Student.objects.filter(
            attendance_records__subject__in=subjects
        ).distinct()

    else:
        raise PermissionDenied

    summaries = []

    for student in students:
        attendance_records = Attendance.objects.filter(
            student=student
        )

        if request.user.role == "FACULTY":
            attendance_records = attendance_records.filter(
                subject__faculty__user=request.user
            )

        total = attendance_records.count()

        present = attendance_records.filter(
            status="PRESENT"
        ).count()

        percentage = (
            round((present / total) * 100, 2)
            if total
            else 0
        )

        summaries.append({
            "student": student,
            "total": total,
            "present": present,
            "absent": total - present,
            "percentage": percentage,
            "low_attendance": (
                total > 0
                and percentage < ATTENDANCE_THRESHOLD
            ),
        })

    return render(
        request,
        "attendance/summary.html",
        {
            "summaries": summaries,
            "threshold": ATTENDANCE_THRESHOLD,
        },
    )
