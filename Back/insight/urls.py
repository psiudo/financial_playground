# Back/insight/urls.py
from django.urls import path
from . import views

app_name = 'insight'

urlpatterns = [
    path('profile/',                       views.profile,          name='profile'),
    path('<int:stock_id>/analyze/',        views.collect_comments, name='collect_comments'),
    path('<int:stock_id>/perform/',        views.perform_analysis, name='perform_analysis'),
    path('<int:stock_id>/refresh/',        views.refresh_comments, name='refresh_comments'),
    path('<int:stock_id>/status/',         views.analysis_status,  name='analysis_status'),
    path('<int:stock_id>/delete/',         views.delete_stock,     name='delete_stock'),
]
