from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, ProductReviewViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'reviews', ProductReviewViewSet, basename='productreview')

urlpatterns = [
    path('api/', include(router.urls)),
]