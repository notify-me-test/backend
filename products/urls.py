from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, ProductReviewViewSet, ProductSearchView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'reviews', ProductReviewViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/search/', ProductSearchView.as_view(), name='product-search'),
]