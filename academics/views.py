from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import (
    CourseForm,
    FacultyProfileForm,
    ProgrammeForm,
    SemesterForm,
    StudentForm,
    SubjectForm,
)
from .models import Course, FacultyProfile, Programme, Semester, Student, Subject


def is_admin_user(user):
    """Return True for the project's admin role or a Django superuser."""
    return user.is_authenticated and (
        getattr(user, "role", "") == "ADMIN" or user.is_superuser
    )


def students_visible_to(user):
    """Scope student records to the signed-in user's role."""
    qs = Student.objects.select_related("programme", "course", "semester", "user")

    if is_admin_user(user):
        return qs

    role = getattr(user, "role", "")
    if role == "FACULTY":
        # Students enrolled in the same course AND semester as a subject
        # assigned to this faculty member.
        return qs.filter(
            course__subjects__faculty__user=user,
            course__subjects__semester_id=F("semester_id"),
        ).distinct()

    if role == "STUDENT":
        return qs.filter(user=user)

    return qs.none()


def subjects_visible_to(user):
    """Scope subject records to all subjects relevant to this user."""
    qs = Subject.objects.select_related(
        "course", "course__programme", "semester", "faculty", "faculty__user"
    )

    if is_admin_user(user):
        return qs

    role = getattr(user, "role", "")
    if role == "FACULTY":
        return qs.filter(faculty__user=user)

    if role == "STUDENT":
        student = Student.objects.filter(user=user).only("course_id", "semester_id").first()
        if student:
            return qs.filter(course_id=student.course_id, semester_id=student.semester_id)

    return qs.none()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only administrators may create, edit, or delete academic records."""

    def test_func(self):
        return is_admin_user(self.request.user)


class AcademicListView(LoginRequiredMixin, ListView):
    """Authenticated users can view role-scoped lists; only admins can manage."""

    template_name = "academics/list.html"
    context_object_name = "objects"
    page_title = "Academic records"
    create_url = ""
    update_url = ""
    delete_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": self.page_title,
            "create_url": self.create_url,
            "update_url": self.update_url,
            "delete_url": self.delete_url,
            "can_manage": is_admin_user(self.request.user),
            "role": "ADMIN" if is_admin_user(self.request.user) else getattr(self.request.user, "role", ""),
        })
        return context


class AcademicCreateView(AdminRequiredMixin, CreateView):
    template_name = "academics/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["cancel_url"] = self.list_url
        return context


class AcademicUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "academics/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["cancel_url"] = self.list_url
        return context


class AcademicDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "academics/confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["cancel_url"] = self.cancel_url
        return context


# PROGRAMMES
class ProgrammeListView(AcademicListView):
    model = Programme
    page_title = "Programmes"
    create_url = "academics:programme_create"
    update_url = "academics:programme_update"
    delete_url = "academics:programme_delete"

    def get_queryset(self):
        user = self.request.user
        if is_admin_user(user):
            return Programme.objects.all().order_by("name")
        if getattr(user, "role", "") == "FACULTY":
            return Programme.objects.filter(
                courses__subjects__faculty__user=user
            ).distinct().order_by("name")
        if getattr(user, "role", "") == "STUDENT":
            return Programme.objects.filter(students__user=user).distinct().order_by("name")
        return Programme.objects.none()


class ProgrammeCreateView(AcademicCreateView):
    model = Programme
    form_class = ProgrammeForm
    page_title = "Add Programme"
    list_url = "academics:programme_list"
    success_url = reverse_lazy("academics:programme_list")


class ProgrammeUpdateView(AcademicUpdateView):
    model = Programme
    form_class = ProgrammeForm
    page_title = "Edit Programme"
    list_url = "academics:programme_list"
    success_url = reverse_lazy("academics:programme_list")


class ProgrammeDeleteView(AcademicDeleteView):
    model = Programme
    page_title = "Delete Programme"
    cancel_url = "academics:programme_list"
    success_url = reverse_lazy("academics:programme_list")


# COURSES
class CourseListView(AcademicListView):
    model = Course
    page_title = "Courses"
    create_url = "academics:course_create"
    update_url = "academics:course_update"
    delete_url = "academics:course_delete"

    def get_queryset(self):
        user = self.request.user
        qs = Course.objects.select_related("programme")
        if is_admin_user(user):
            return qs.order_by("name")
        if getattr(user, "role", "") == "FACULTY":
            return qs.filter(subjects__faculty__user=user).distinct().order_by("name")
        if getattr(user, "role", "") == "STUDENT":
            return qs.filter(students__user=user).distinct().order_by("name")
        return qs.none()


class CourseCreateView(AcademicCreateView):
    model = Course
    form_class = CourseForm
    page_title = "Add Course"
    list_url = "academics:course_list"
    success_url = reverse_lazy("academics:course_list")


class CourseUpdateView(AcademicUpdateView):
    model = Course
    form_class = CourseForm
    page_title = "Edit Course"
    list_url = "academics:course_list"
    success_url = reverse_lazy("academics:course_list")


class CourseDeleteView(AcademicDeleteView):
    model = Course
    page_title = "Delete Course"
    cancel_url = "academics:course_list"
    success_url = reverse_lazy("academics:course_list")


# SEMESTERS
class SemesterListView(AcademicListView):
    model = Semester
    page_title = "Semesters"
    create_url = "academics:semester_create"
    update_url = "academics:semester_update"
    delete_url = "academics:semester_delete"

    def get_queryset(self):
        user = self.request.user
        qs = Semester.objects.all()
        if is_admin_user(user):
            return qs.order_by("academic_year", "number")
        if getattr(user, "role", "") == "FACULTY":
            return qs.filter(subjects__faculty__user=user).distinct().order_by("academic_year", "number")
        if getattr(user, "role", "") == "STUDENT":
            return qs.filter(students__user=user).distinct().order_by("academic_year", "number")
        return qs.none()


class SemesterCreateView(AcademicCreateView):
    model = Semester
    form_class = SemesterForm
    page_title = "Add Semester"
    list_url = "academics:semester_list"
    success_url = reverse_lazy("academics:semester_list")


class SemesterUpdateView(AcademicUpdateView):
    model = Semester
    form_class = SemesterForm
    page_title = "Edit Semester"
    list_url = "academics:semester_list"
    success_url = reverse_lazy("academics:semester_list")


class SemesterDeleteView(AcademicDeleteView):
    model = Semester
    page_title = "Delete Semester"
    cancel_url = "academics:semester_list"
    success_url = reverse_lazy("academics:semester_list")


# FACULTY DIRECTORY
class FacultyListView(AcademicListView):
    model = FacultyProfile
    page_title = "Faculty"
    create_url = "academics:faculty_create"
    update_url = "academics:faculty_update"
    delete_url = "academics:faculty_delete"

    def get_queryset(self):
        user = self.request.user
        qs = FacultyProfile.objects.select_related("user")
        if is_admin_user(user):
            return qs.order_by("user__first_name", "user__last_name", "user__username")
        if getattr(user, "role", "") == "FACULTY":
            return qs.filter(user=user)
        if getattr(user, "role", "") == "STUDENT":
            student = Student.objects.filter(user=user).only("course_id", "semester_id").first()
            if student:
                return qs.filter(
                    subjects__course_id=student.course_id,
                    subjects__semester_id=student.semester_id,
                ).distinct()
        return qs.none()


class FacultyCreateView(AcademicCreateView):
    model = FacultyProfile
    form_class = FacultyProfileForm
    page_title = "Add Faculty Profile"
    list_url = "academics:faculty_list"
    success_url = reverse_lazy("academics:faculty_list")


class FacultyUpdateView(AcademicUpdateView):
    model = FacultyProfile
    form_class = FacultyProfileForm
    page_title = "Edit Faculty Profile"
    list_url = "academics:faculty_list"
    success_url = reverse_lazy("academics:faculty_list")


class FacultyDeleteView(AcademicDeleteView):
    model = FacultyProfile
    page_title = "Delete Faculty Profile"
    cancel_url = "academics:faculty_list"
    success_url = reverse_lazy("academics:faculty_list")


# STUDENT DIRECTORY
class StudentListView(AcademicListView):
    model = Student
    page_title = "Students"
    create_url = "academics:student_create"
    update_url = "academics:student_update"
    delete_url = "academics:student_delete"

    def get_base_queryset(self):
        return students_visible_to(self.request.user)

    def get_queryset(self):
        queryset = self.get_base_queryset()
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(roll_number__icontains=search)
                | Q(email__icontains=search)
                | Q(user__username__icontains=search)
            )
        programme = self.request.GET.get("programme", "")
        course = self.request.GET.get("course", "")
        semester = self.request.GET.get("semester", "")
        if programme:
            queryset = queryset.filter(programme_id=programme)
        if course:
            queryset = queryset.filter(course_id=course)
        if semester:
            queryset = queryset.filter(semester_id=semester)
        return queryset.order_by("roll_number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base = self.get_base_queryset()
        context.update({
            "search_query": self.request.GET.get("q", ""),
            "selected_programme": self.request.GET.get("programme", ""),
            "selected_course": self.request.GET.get("course", ""),
            "selected_semester": self.request.GET.get("semester", ""),
            "programmes": Programme.objects.filter(students__in=base).distinct(),
            "courses": Course.objects.filter(students__in=base).distinct(),
            "semesters": Semester.objects.filter(students__in=base).distinct(),
            "total_results": self.object_list.count(),
        })
        return context


# SUBJECT DIRECTORY
class SubjectListView(AcademicListView):
    model = Subject
    page_title = "Subjects"
    create_url = "academics:subject_create"
    update_url = "academics:subject_update"
    delete_url = "academics:subject_delete"

    def get_base_queryset(self):
        return subjects_visible_to(self.request.user)

    def get_queryset(self):
        queryset = self.get_base_queryset()
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(course__name__icontains=search)
            )
        course = self.request.GET.get("course", "")
        semester = self.request.GET.get("semester", "")
        faculty = self.request.GET.get("faculty", "")
        if course:
            queryset = queryset.filter(course_id=course)
        if semester:
            queryset = queryset.filter(semester_id=semester)
        if faculty and is_admin_user(self.request.user):
            queryset = queryset.filter(faculty_id=faculty)
        return queryset.order_by("code")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base = self.get_base_queryset()
        admin = is_admin_user(self.request.user)
        context.update({
            "search_query": self.request.GET.get("q", ""),
            "selected_course": self.request.GET.get("course", ""),
            "selected_semester": self.request.GET.get("semester", ""),
            "selected_faculty": self.request.GET.get("faculty", ""),
            "courses": Course.objects.filter(subjects__in=base).distinct(),
            "semesters": Semester.objects.filter(subjects__in=base).distinct(),
            "faculties": FacultyProfile.objects.filter(subjects__in=base).select_related("user").distinct() if admin else FacultyProfile.objects.none(),
        })
        return context


# STUDENT CRUD (ADMIN ONLY)
class StudentCreateView(AcademicCreateView):
    model = Student
    form_class = StudentForm
    page_title = "Add Student"
    list_url = "academics:student_list"
    success_url = reverse_lazy("academics:student_list")


class StudentUpdateView(AcademicUpdateView):
    model = Student
    form_class = StudentForm
    page_title = "Edit Student"
    list_url = "academics:student_list"
    success_url = reverse_lazy("academics:student_list")


class StudentDeleteView(AcademicDeleteView):
    model = Student
    page_title = "Delete Student"
    cancel_url = "academics:student_list"
    success_url = reverse_lazy("academics:student_list")


# SUBJECT CRUD (ADMIN ONLY)
class SubjectCreateView(AcademicCreateView):
    model = Subject
    form_class = SubjectForm
    page_title = "Add Subject"
    list_url = "academics:subject_list"
    success_url = reverse_lazy("academics:subject_list")


class SubjectUpdateView(AcademicUpdateView):
    model = Subject
    form_class = SubjectForm
    page_title = "Edit Subject"
    list_url = "academics:subject_list"
    success_url = reverse_lazy("academics:subject_list")


class SubjectDeleteView(AcademicDeleteView):
    model = Subject
    page_title = "Delete Subject"
    cancel_url = "academics:subject_list"
    success_url = reverse_lazy("academics:subject_list")
