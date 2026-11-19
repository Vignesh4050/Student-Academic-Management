from django.contrib import admin
from .models import (
    Programme,
    Course,
    Semester,
    FacultyProfile,
    Student,
    Subject,
)


admin.site.register(Programme)
admin.site.register(Course)
admin.site.register(Semester)
admin.site.register(FacultyProfile)
admin.site.register(Student)
admin.site.register(Subject)