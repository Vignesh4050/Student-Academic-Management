from django.urls import path
from . import views
from .views import (
    ProgrammeListView,
    ProgrammeCreateView,
    ProgrammeUpdateView,
    ProgrammeDeleteView,
    CourseListView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView,
    SemesterListView,
    SemesterCreateView,
    SemesterUpdateView,
    SemesterDeleteView,
    FacultyListView,
    FacultyCreateView,
    FacultyUpdateView,
    FacultyDeleteView,
    StudentListView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
    SubjectListView,
    SubjectCreateView,
    SubjectUpdateView,
    SubjectDeleteView,
)

app_name = "academics"
urlpatterns = [
    # Programmes
    path('programmes/', ProgrammeListView.as_view(),
         name='programme_list'),
    path('programmes/add/', ProgrammeCreateView.as_view(),
         name='programme_create'),
    path('programmes/<int:pk>/edit/', ProgrammeUpdateView.as_view(),
         name='programme_update'),
    path('programmes/<int:pk>/delete/', ProgrammeDeleteView.as_view(),
         name='programme_delete'),

    # Courses
    path('courses/', CourseListView.as_view(),
         name='course_list'),
    path('courses/add/', CourseCreateView.as_view(),
         name='course_create'),
    path('courses/<int:pk>/edit/', CourseUpdateView.as_view(),
         name='course_update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(),
         name='course_delete'),

    # Semesters
    path('semesters/', SemesterListView.as_view(),
         name='semester_list'),
    path('semesters/add/', SemesterCreateView.as_view(),
         name='semester_create'),
    path('semesters/<int:pk>/edit/', SemesterUpdateView.as_view(),
         name='semester_update'),
    path('semesters/<int:pk>/delete/', SemesterDeleteView.as_view(),
         name='semester_delete'),

    # Faculty
    path('faculty/', FacultyListView.as_view(),
         name='faculty_list'),
    path('faculty/add/', FacultyCreateView.as_view(),
         name='faculty_create'),
    path('faculty/<int:pk>/edit/', FacultyUpdateView.as_view(),
         name='faculty_update'),
    path('faculty/<int:pk>/delete/', FacultyDeleteView.as_view(),
         name='faculty_delete'),

    # Students
    path('students/', StudentListView.as_view(),
         name='student_list'),
    path('students/add/', StudentCreateView.as_view(),
         name='student_create'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(),
         name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(),
         name='student_delete'),

    # Subjects
    path('subjects/', SubjectListView.as_view(),
         name='subject_list'),
    path('subjects/add/', SubjectCreateView.as_view(),
         name='subject_create'),
    path('subjects/<int:pk>/edit/', SubjectUpdateView.as_view(),
         name='subject_update'),
    path('subjects/<int:pk>/delete/', SubjectDeleteView.as_view(),
         name='subject_delete'),
]