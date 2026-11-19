from django.urls import path
from . import views
from .views import (
    DashboardView,
    PerformanceReportView,
    ExportPerformanceCSVView,
)

app_name = "reports"

urlpatterns = [
    
    path("", DashboardView.as_view(), name="dashboard"),

    path("performance/", views.PerformanceReportView.as_view(), name="performance_reports"),

    path("performance/export/csv/",ExportPerformanceCSVView.as_view(),name="export_performance_csv"),
]