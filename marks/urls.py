from django.urls import path
from . import views

urlpatterns = [
    path("", views.marks_list, name="marks_list"),
    path("add/", views.marks_create, name="marks_create"),
    path("edit/<int:pk>/", views.marks_update, name="marks_update"),
    path("delete/<int:pk>/", views.marks_delete, name="marks_delete"),
]

#python manage.py shell -c "import marks.urls; print('File:', marks.urls.__file__); print('URL patterns:', marks.urls.urlpatterns)"
