from django.conf import settings
from django.db import models


class Programme(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Semester(models.Model):
    number = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'academic_year'],
                name='unique_semester_year'
            )
        ]

    def __str__(self):
        return f"Semester {self.number} - {self.academic_year}"


class FacultyProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )

    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile'
    )

    roll_number = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name='students'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='students'
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name='students'
    )

    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.roll_number} - {self.full_name}"


class Subject(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='subjects'
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name='subjects'
    )

    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)

    max_internal_marks = models.PositiveSmallIntegerField(default=20)
    max_exam_marks = models.PositiveSmallIntegerField(default=80)

    def __str__(self):
        return f"{self.code} - {self.name}"