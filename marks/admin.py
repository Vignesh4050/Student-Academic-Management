from django.contrib import admin
from .models import Marks


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject',
        'internal_marks',
        'exam_marks',
        'updated_at',
    )

    list_filter = ('subject',)

    search_fields = (
        'student__roll_number',
        'student__full_name',
        'subject__name',
    )