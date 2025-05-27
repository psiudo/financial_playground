# back/community/urls.py
from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('',                views.post_list,   name='post_list'),
    path('write/',          views.post_create, name='post_create'),
    path('<int:post_id>/',  views.post_detail, name='post_detail'),
    path('<int:post_id>/<str:reaction_type>/', views.toggle_reaction, name='toggle_reaction'),

    # 웹 댓글 작성 (새로 추가)
    path('comments/create/', views.comment_create, name='comment_create'),
    path('comments/<int:comment_id>/edit/', views.comment_update, name='comment_update'),
    path('comments/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('comments/<int:comment_id>/like/', views.comment_toggle_like, name='comment_toggle_like'),


    # API 전용
    path('comments/', views.CommentListCreateView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view(), name='comment_detail'),
]
