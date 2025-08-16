from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, ProductImage, ProductReview
from .serializers import (
    ProductSerializer, CategorySerializer, ProductImageSerializer,
    ProductReviewSerializer, ProductListSerializer
)
from .services import ProductService
from .repositories import ProductRepository, CategoryRepository, ProductReviewRepository

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject repositories
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.review_repository = ProductReviewRepository()
        # Create service with repository dependencies
        self.product_service = ProductService(
            product_repository=self.product_repository,
            category_repository=self.category_repository,
            review_repository=self.review_repository
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        # Extract HTTP parameters (ViewSet responsibility)
        filters = {
            'category': self.request.query_params.get('category'),
            'search': self.request.query_params.get('search'),
            'min_price': self.request.query_params.get('min_price'),
            'max_price': self.request.query_params.get('max_price')
        }
        
        # Delegate business logic to service (Service responsibility)
        return self.product_service.get_products_with_filters_and_enrichment(filters)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        product = self.get_object()
        new_stock = request.data.get('stock_quantity')
        
        result = self.product_service.update_product_stock(product.id, new_stock)
        
        # Check if there was an error and return appropriate response
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        threshold = request.query_params.get('threshold', 10)
        
        products = self.product_service.get_low_stock_products(threshold)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject repositories
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.review_repository = ProductReviewRepository()
        # Create service with repository dependencies
        self.product_service = ProductService(
            product_repository=self.product_repository,
            category_repository=self.category_repository,
            review_repository=self.review_repository
        )
    
    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        
        # Delegate business logic to service
        return self.product_service.get_reviews_by_product(product_id)

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject repositories
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.review_repository = ProductReviewRepository()
        # Create service with repository dependencies
        self.product_service = ProductService(
            product_repository=self.product_repository,
            category_repository=self.category_repository,
            review_repository=self.review_repository
        )
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        
        # Delegate search logic to service
        return self.product_service.search_products(query)