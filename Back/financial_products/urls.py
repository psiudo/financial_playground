# Back/financial_products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view()),
    path('subscribed/', views.subscribed_products),
    path('recommend/', views.recommend_products, name='recommend_products'),
    path('subscribe/<str:product_id>/', views.SubscribeProductView.as_view()),
    path('<str:product_id>/', views.ProductDetailView.as_view()),
]

