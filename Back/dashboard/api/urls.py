# dashboard/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("summary/", views.DashboardAPIView.as_view(), name="dashboard-summary"),
]
