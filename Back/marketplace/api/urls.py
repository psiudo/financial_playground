# Back/marketplace/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.MarketListingListCreateAPIView.as_view(),
         name="listing-list-create"),
    path("<int:pk>/", views.MarketListingRetrieveUpdateDestroyAPIView.as_view(),
         name="listing-detail"),
    path("<int:pk>/purchase/", views.PurchaseAPIView.as_view(),
         name="listing-purchase"),
    path("purchases/", views.PurchaseListAPIView.as_view(),
         name="purchase-list"),
]
