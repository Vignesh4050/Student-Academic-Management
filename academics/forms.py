from django import forms

from .models import (
    Programme,
    Course,
    Semester,
    FacultyProfile,
    Student,
    Subject,
)


class StyledModelForm(forms.ModelForm):
    """
    Add Bootstrap styling to generated form fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class ProgrammeForm(StyledModelForm):
    class Meta:
        model = Programme
        fields = ['name', 'code', 'description']


class CourseForm(StyledModelForm):
    class Meta:
        model = Course
        fields = ['programme', 'name', 'code']


class SemesterForm(StyledModelForm):
    class Meta:
        model = Semester
        fields = ['number', 'academic_year']


class FacultyProfileForm(StyledModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['user', 'department']


class StudentForm(StyledModelForm):
    class Meta:
        model = Student
        fields = [
            'user',
            'roll_number',
            'full_name',
            'email',
            'programme',
            'course',
            'semester',
            'date_of_birth',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }


class SubjectForm(StyledModelForm):
    class Meta:
        model = Subject
        fields = [
            'course',
            'semester',
            'faculty',
            'name',
            'code',
            'max_internal_marks',
            'max_exam_marks',
        ]