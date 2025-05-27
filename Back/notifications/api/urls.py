# notifications/api/urls.py
from django.urls import path
from .views import (
    NotificationListView,
    notification_mark_read,
    notification_mark_all_read,
)

urlpatterns = [
    path("",             NotificationListView.as_view()),
    path("<int:pk>/read/", notification_mark_read),
    path("read-all/",      notification_mark_all_read),
]
