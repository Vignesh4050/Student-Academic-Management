from django import forms

from academics.models import Student, Subject
from .models import Marks


class MarksForm(forms.ModelForm):

    class Meta:
        model = Marks
        fields = [
            "student",
            "subject",
            "internal_marks",
            "exam_marks",
        ]

        widgets = {
            "student": forms.Select(
                attrs={"class": "form-select"}
            ),
            "subject": forms.Select(
                attrs={"class": "form-select"}
            ),
            "internal_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "exam_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields["subject"].queryset = Subject.objects.none()
            self.fields["student"].queryset = Student.objects.none()
            return

        if user.role == "ADMIN":
            subjects = Subject.objects.all()

        elif user.role == "FACULTY":
            subjects = Subject.objects.filter(
                faculty__user=user
            )

        else:
            subjects = Subject.objects.none()

        subjects = subjects.select_related(
            "course",
            "semester"
        ).order_by("name")

        self.fields["subject"].queryset = subjects

        self.fields["student"].queryset = Student.objects.filter(
            course__in=subjects.values("course_id"),
            semester__in=subjects.values("semester_id"),
        ).distinct().order_by("roll_number")

    def clean(self):
        cleaned_data = super().clean()

        student = cleaned_data.get("student")
        subject = cleaned_data.get("subject")
        internal_marks = cleaned_data.get("internal_marks")
        exam_marks = cleaned_data.get("exam_marks")

        if student and subject:

            # Check that the student is enrolled in
            # the selected subject's course and semester.
            if (
                student.course_id != subject.course_id
                or student.semester_id != subject.semester_id
            ):
                raise forms.ValidationError(
                    "The selected student is not enrolled "
                    "in this subject's course and semester."
                )

            # Check maximum internal marks.
            if (
                internal_marks is not None
                and internal_marks > subject.max_internal_marks
            ):
                self.add_error(
                    "internal_marks",
                    f"Maximum internal marks are "
                    f"{subject.max_internal_marks}."
                )

            # Check maximum examination marks.
            if (
                exam_marks is not None
                and exam_marks > subject.max_exam_marks
            ):
                self.add_error(
                    "exam_marks",
                    f"Maximum examination marks are "
                    f"{subject.max_exam_marks}."
                )

            # Prevent duplicate marks records.
            existing_record = Marks.objects.filter(
                student=student,
                subject=subject,
            )

            if self.instance.pk:
                existing_record = existing_record.exclude(
                    pk=self.instance.pk
                )

            if existing_record.exists():
                raise forms.ValidationError(
                    "A marks record already exists for this "
                    "student and subject. Use Edit to update it."
                )

        return cleaned_data