from django import forms
from django.forms import formset_factory

from academics.models import Subject
from .models import Attendance


class AttendanceSessionForm(forms.Form):

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        label="Select Subject"
    )

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
        label="Attendance Date"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["subject"].queryset = (
            Subject.objects.select_related(
                "course",
                "semester"
            ).order_by("name")
        )

        self.fields["subject"].widget.attrs.update({
            "class": "form-select"
        })

        self.fields["date"].widget.attrs.update({
            "class": "form-control"
        })


class AttendanceEntryForm(forms.Form):

    student_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    status = forms.ChoiceField(
        choices=Attendance.STATUS_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select"}
        )
    )


AttendanceEntryFormSet = formset_factory(
    AttendanceEntryForm,
    extra=0
)