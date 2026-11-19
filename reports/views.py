import csv
from collections import defaultdict
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from academics.models import Course, Programme, Student, Subject
from attendance.models import Attendance
from marks.models import Marks

LOW_MARKS_THRESHOLD = 40
LOW_ATTENDANCE_THRESHOLD = 75


def scoped_records(user):
    """Return student and subject querysets restricted to the user's role."""
    students = Student.objects.select_related("programme", "course", "semester", "user")
    subjects = Subject.objects.select_related("course", "semester", "faculty__user")
    role = getattr(user, "role", "")

    if role == "ADMIN" or user.is_superuser:
        return students, subjects

    if role == "FACULTY":
        subjects = subjects.filter(faculty__user=user)
        students = students.filter(
            course__subjects__faculty__user=user,
            course__subjects__semester_id=F("semester_id"),
        ).distinct()
        return students, subjects

    if role == "STUDENT":
        student = students.filter(user=user).first()
        if not student:
            return students.none(), subjects.none()
        return (
            students.filter(pk=student.pk),
            subjects.filter(course_id=student.course_id, semester_id=student.semester_id),
        )

    return students.none(), subjects.none()


def report_rows(students, subjects):
    student_ids = list(students.values_list("id", flat=True))
    subject_ids = list(subjects.values_list("id", flat=True))
    marks = Marks.objects.filter(
        student_id__in=student_ids,
        subject_id__in=subject_ids,
    ).select_related("student", "subject")

    scores = defaultdict(list)
    for mark in marks:
        maximum = float(mark.maximum_marks or 0)
        if maximum > 0:
            scores[mark.student_id].append(float(mark.percentage))

    attendance_totals = defaultdict(lambda: [0, 0])
    for record in Attendance.objects.filter(
        student_id__in=student_ids,
        subject_id__in=subject_ids,
    ):
        attendance_totals[record.student_id][1] += 1
        if record.status == "PRESENT":
            attendance_totals[record.student_id][0] += 1

    rows = []
    for student in students.order_by("roll_number"):
        values = scores[student.id]
        present, total = attendance_totals[student.id]
        rows.append({
            "student": student,
            "average_marks": round(sum(values) / len(values), 2) if values else 0,
            "attendance_percentage": round(present / total * 100, 2) if total else 0,
            "marks_records": len(values),
        })
    return rows


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        role = "ADMIN" if user.is_superuser else getattr(user, "role", "")
        students, subjects = scoped_records(user)
        rows = report_rows(students, subjects)

        mark_records = list(
            Marks.objects.filter(student__in=students, subject__in=subjects)
            .select_related("student", "subject")
        )
        marks_count = len(mark_records)
        average_percentage = round(
            sum(float(mark.percentage) for mark in mark_records) / marks_count, 2
        ) if marks_count else 0

        attendance_records = Attendance.objects.filter(
            student__in=students, subject__in=subjects
        )
        attendance_total = attendance_records.count()
        present_count = attendance_records.filter(status="PRESENT").count()
        attendance_percentage = round(present_count / attendance_total * 100, 2) if attendance_total else 0

        subject_averages = []
        for subject in subjects.order_by("code"):
            values = [float(mark.percentage) for mark in mark_records if mark.subject_id == subject.id]
            if values:
                subject_averages.append({
                    "name": subject.name,
                    "average": round(sum(values) / len(values), 2),
                })

        grade_counts = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for mark in mark_records:
            grade = mark.grade
            if grade in grade_counts:
                grade_counts[grade] += 1

        student_by_id = {student.id: student for student in students}
        attendance_by_subject_student = defaultdict(lambda: [0, 0])
        for record in attendance_records.select_related("student", "subject"):
            item = attendance_by_subject_student[(record.subject_id, record.student_id)]
            item[1] += 1
            if record.status == "PRESENT":
                item[0] += 1

        subject_by_id = {subject.id: subject for subject in subjects}
        attendance_summary = []
        for (subject_id, student_id), (present, total) in attendance_by_subject_student.items():
            student = student_by_id.get(student_id)
            subject = subject_by_id.get(subject_id)
            if not student or not subject:
                continue
            percentage = round(present / total * 100, 2) if total else 0
            attendance_summary.append({
                "roll_number": student.roll_number,
                "student_name": student.full_name,
                "subject_name": subject.name,
                "present": present,
                "absent": total - present,
                "percentage": percentage,
                "low_attendance": percentage < LOW_ATTENDANCE_THRESHOLD,
            })
        attendance_summary.sort(key=lambda item: (item["student_name"], item["subject_name"]))

        if role == "STUDENT":
            role_title = "Student Dashboard"
        elif role == "FACULTY":
            role_title = "Faculty Dashboard"
        else:
            role_title = "Administrator Dashboard"

        if role in ("ADMIN",) or user.is_superuser:
            total_programmes = Programme.objects.count()
            total_courses = Course.objects.count()
        else:
            total_programmes = students.values("programme_id").distinct().count()
            total_courses = subjects.values("course_id").distinct().count()

        student_row = rows[0] if role == "STUDENT" and rows else None
        context = {
            "role": role,
            "role_title": role_title,
            "today": timezone.localdate(),
            "total_students": students.count(),
            "total_programmes": total_programmes,
            "total_courses": total_courses,
            "total_subjects": subjects.count(),
            "average_percentage": average_percentage,
            "attendance_percentage": attendance_percentage,
            "present_count": present_count,
            "attendance_total": attendance_total,
            "marks_count": marks_count,
            "grade_counts": grade_counts,
            "subject_averages": subject_averages,
            "attendance_summary": attendance_summary,
            "student_average": student_row["average_marks"] if student_row else average_percentage,
        }
        return render(request, "reports/dashboard.html", context)


class PerformanceReportView(LoginRequiredMixin, View):
    def get(self, request):
        students, subjects = scoped_records(request.user)
        rows = report_rows(students, subjects)
        context = {
            "rows": rows,
            "low_marks_threshold": LOW_MARKS_THRESHOLD,
            "low_attendance_threshold": LOW_ATTENDANCE_THRESHOLD,
            "low_marks_count": sum(
                row["average_marks"] < LOW_MARKS_THRESHOLD
                for row in rows if row["marks_records"] > 0
            ),
            "low_attendance_count": sum(
                row["attendance_percentage"] < LOW_ATTENDANCE_THRESHOLD
                for row in rows if row["attendance_percentage"] > 0
            ),
        }
        return render(request, "reports/performance_reports.html", context)


class ExportPerformanceCSVView(LoginRequiredMixin, View):
    def get(self, request):
        students, subjects = scoped_records(request.user)
        rows = report_rows(students, subjects)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_performance_report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Roll Number", "Student Name", "Programme", "Course", "Semester",
            "Average Marks (%)", "Attendance (%)", "Marks Records",
        ])
        for row in rows:
            student = row["student"]
            writer.writerow([
                student.roll_number,
                student.full_name,
                student.programme.name,
                student.course.name,
                student.semester.number,
                row["average_marks"],
                row["attendance_percentage"],
                row["marks_records"],
            ])
        return response
