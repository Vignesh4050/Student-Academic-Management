from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject',
        'date',
        'status',
    )

    list_filter = (
        'subject',
        'date',
        'status',
    )

    search_fields = (
        'student__roll_number',
        'student__full_name',
        'subject__name',
    )