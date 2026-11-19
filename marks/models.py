from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from academics.models import Student, Subject


class Marks(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="marks_records"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="marks_records"
    )

    internal_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    exam_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject"],
                name="unique_student_subject_marks"
            )
        ]

    def clean(self):
        super().clean()

        if self.subject_id:
            if self.internal_marks is not None:
                if self.internal_marks > self.subject.max_internal_marks:
                    raise ValidationError({
                        "internal_marks": (
                            "Internal marks cannot exceed "
                            f"{self.subject.max_internal_marks}."
                        )
                    })

            if self.exam_marks is not None:
                if self.exam_marks > self.subject.max_exam_marks:
                    raise ValidationError({
                        "exam_marks": (
                            "Examination marks cannot exceed "
                            f"{self.subject.max_exam_marks}."
                        )
                    })

    @property
    def total_marks(self):
        return self.internal_marks + self.exam_marks

    @property
    def maximum_marks(self):
        return (
            self.subject.max_internal_marks
            + self.subject.max_exam_marks
        )

    @property
    def percentage(self):
        if self.maximum_marks == 0:
            return 0

        return round(
            float(self.total_marks) / self.maximum_marks * 100,
            2
        )

    @property
    def grade(self):
        percentage = self.percentage

        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        else:
            return "F"

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code}"