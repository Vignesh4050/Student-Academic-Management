from django.db import models
from django.db.models import Q
from academics.models import Student, Subject


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'date'],
                name='unique_student_subject_attendance_date'
            ),
            models.CheckConstraint(
                condition=Q(status__in=['PRESENT', 'ABSENT']),
                name='valid_attendance_status'
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.roll_number} - "
            f"{self.subject.code} - {self.date}"
        )