
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from academics.models import (
    Programme,
    Course,
    Semester,
    FacultyProfile,
    Student,
    Subject,
)
from marks.models import Marks
from attendance.models import Attendance


User = get_user_model()


class Command(BaseCommand):
    help = "Create dummy data for Student Academic Management"

    def handle(self, *args, **kwargs):

        self.stdout.write("Creating dummy dataset...")

        # 1. ADMIN ACCOUNT
        admin, created = User.objects.get_or_create(
            username="admin1",
            defaults={
                "first_name": "System",
                "last_name": "Admin",
                "email": "admin@example.com",
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            admin.set_password("Admin@123")

        admin.role = "ADMIN"
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        # 2. FACULTY ACCOUNTS AND PROFILES
        faculty_profiles = []

        for i in range(1, 3):
            user, created = User.objects.get_or_create(
                username=f"faculty{i}",
                defaults={
                    "first_name": f"Faculty{i}",
                    "last_name": "Demo",
                    "email": f"faculty{i}@example.com",
                    "role": "FACULTY",
                },
            )

            if created:
                user.set_password("Faculty@123")
                user.save()

            profile, _ = FacultyProfile.objects.get_or_create(
                user=user,
                defaults={
                    "department": "Computer Science"
                },
            )

            faculty_profiles.append(profile)

        # 3. PROGRAMME
        programme, _ = Programme.objects.get_or_create(
            code="BSC",
            defaults={
                "name": "Bachelor of Science",
                "description": "Undergraduate programme",
            },
        )

        # 4. COURSE
        course, _ = Course.objects.get_or_create(
            code="BSC-CS",
            defaults={
                "programme": programme,
                "name": "B.Sc. Computer Science",
            },
        )

        # 5. SEMESTER
        semester, _ = Semester.objects.get_or_create(
            number=1,
            academic_year="2026-27",
        )

        # 6. SUBJECTS
        subject_data = [
            ("Python Programming", "CS101", faculty_profiles[0]),
            ("Database Management", "CS102", faculty_profiles[1]),
            ("Computer Networks", "CS103", faculty_profiles[0]),
        ]

        subjects = []

        for name, code, faculty in subject_data:

            subject, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    "course": course,
                    "semester": semester,
                    "faculty": faculty,
                    "name": name,
                    "max_internal_marks": 20,
                    "max_exam_marks": 80,
                },
            )

            subjects.append(subject)

        # 7. STUDENT ACCOUNTS AND PROFILES
        student_names = [
            "Aarav Sharma",
            "Riya Naik",
            "Aditya Patil",
            "Ananya Desai",
            "Rahul Sawant",
            "Sneha Kamat",
            "Karan Shah",
            "Priya Verma",
            "Rohan Kulkarni",
            "Neha Joshi",
        ]

        students = []

        for i, name in enumerate(student_names, start=1):

            username = f"student{i}"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": name.split()[0],
                    "last_name": name.split()[-1],
                    "email": f"{username}@example.com",
                    "role": "STUDENT",
                },
            )

            if created:
                user.set_password("Student@123")
                user.save()

            student, _ = Student.objects.get_or_create(
                roll_number=f"CS2026{i:03d}",
                defaults={
                    "user": user,
                    "full_name": name,
                    "email": f"{username}@example.com",
                    "programme": programme,
                    "course": course,
                    "semester": semester,
                    "date_of_birth": (
                        date(2005, 1, 1) +
                        timedelta(days=i * 30)
                    ),
                },
            )

            students.append(student)

        # 8. MARKS RECORDS
        for student_index, student in enumerate(students):

            for subject_index, subject in enumerate(subjects):

                internal = Decimal(
                    12 + ((student_index + subject_index) % 9)
                )

                exam = Decimal(
                    55 + ((student_index * 3 + subject_index * 5) % 26)
                )

                Marks.objects.update_or_create(
                    student=student,
                    subject=subject,
                    defaults={
                        "internal_marks": internal,
                        "exam_marks": exam,
                    },
                )

        # 9. ATTENDANCE RECORDS
        today = timezone.localdate()

        for student_index, student in enumerate(students):

            for subject_index, subject in enumerate(subjects):

                for day in range(1, 16):

                    attendance_date = today - timedelta(days=day)

                    status = (
                        "ABSENT"
                        if (student_index + subject_index + day) % 5 == 0
                        else "PRESENT"
                    )

                    Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=attendance_date,
                        defaults={
                            "status": status
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Dummy dataset created successfully!"
            )
        )
