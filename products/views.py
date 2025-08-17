from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, ProductImage, ProductReview
from .serializers import (
    ProductSerializer, CategorySerializer, ProductImageSerializer,
    ProductReviewSerializer, ProductListSerializer
)
from .services import ProductService, CategoryService, ReviewService
from .repositories import ProductRepository, CategoryRepository, ProductReviewRepository
from django.core.exceptions import ValidationError


class CategoryViewSet(viewsets.ViewSet):
    """
    ViewSet with dependency injection for maximum testability.
    """
    
    def __init__(self, category_service=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency injection with fallback to default
        self.category_service = category_service or self._create_default_service()
    
    def _create_default_service(self):
        """Factory method for default service creation."""
        category_repository = CategoryRepository()
        return CategoryService(category_repository)
    
    def list(self, request):
        """GET /categories/ - List all categories."""
        categories = self.category_service.get_all_categories()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """GET /categories/{id}/ - Retrieve single category."""
        try:
            category = self.category_service.get_category_by_id(pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """POST /categories/ - Create new category with validation."""
        try:
            self.category_service.validate_category(request.data)
            category = self.category_service.create_category(request.data)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """PUT /categories/{id}/ - Update category with validation."""
        try:
            self.category_service.validate_category(request.data)
            category = self.category_service.update_category(pk, request.data)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /categories/{id}/ - Delete category."""
        try:
            result = self.category_service.delete_category(pk)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Failed to delete category'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class ProductViewSet(viewsets.ViewSet):
    """
    ViewSet with dependency injection for maximum testability.
    """
    
    def __init__(self, product_service=None, category_service=None, review_service=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency injection with fallback to defaults
        self.product_service = product_service or self._create_default_product_service()
        self.category_service = category_service or self._create_default_category_service()
        self.review_service = review_service or self._create_default_review_service()
    
    def _create_default_product_service(self):
        """Factory method for default product service creation."""
        product_repository = ProductRepository()
        return ProductService(product_repository)
    
    def _create_default_category_service(self):
        """Factory method for default category service creation."""
        category_repository = CategoryRepository()
        return CategoryService(category_repository)
    
    def _create_default_review_service(self):
        """Factory method for default review service creation."""
        review_repository = ProductReviewRepository()
        return ReviewService(review_repository)
    
    def get_serializer_class(self, action_name=None):
        """Dynamic serializer selection."""
        if action_name == 'list' or action_name is None:
            return ProductListSerializer
        return ProductSerializer
    
    def list(self, request):
        """GET /products/ - List products with filtering and enrichment."""
        # Extract query parameters
        filters = {
            'category': request.query_params.get('category'),
            'search': request.query_params.get('search'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'is_active': request.query_params.get('is_active')
        }
        
        # Get filtered and enriched products
        products = self.product_service.get_products_with_filters_and_enrichment(
            filters, self.category_service.category_repository, self.review_service.review_repository
        )
        
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(products, many=True)
        return Response({
            'count': len(products),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """GET /products/{id}/ - Retrieve single product."""
        try:
            product = self.product_service.get_product_by_id(pk)
            serializer_class = self.get_serializer_class('retrieve')
            serializer = serializer_class(product)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """POST /products/ - Create new product."""
        try:
            product = self.product_service.create_product(request.data)
            serializer_class = self.get_serializer_class('create')
            serializer = serializer_class(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """PUT /products/{id}/ - Update product."""
        try:
            product = self.product_service.update_product(pk, request.data)
            serializer_class = self.get_serializer_class('update')
            serializer = serializer_class(product)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /products/{id}/ - Delete product."""
        try:
            result = self.product_service.delete_product(pk)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Failed to delete product'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """POST /products/{id}/update_stock/ - Update product stock."""
        new_stock = request.data.get('stock_quantity')
        
        if new_stock is None:
            return Response({'error': 'stock_quantity is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_stock = int(new_stock)
        except ValueError:
            return Response({'error': 'stock_quantity must be a number'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if new_stock < 0:
            return Response({'error': 'stock_quantity cannot be negative'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        result = self.product_service.update_product_stock(pk, new_stock)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """GET /products/low_stock/ - Get products below threshold."""
        threshold = request.query_params.get('threshold', 10)
        try:
            threshold = int(threshold)
        except ValueError:
            threshold = 10
        
        products = self.product_service.get_low_stock_products(threshold)
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """GET /products/search/ - Search products by name or description."""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response([])
        
        products = self.product_service.search_products(query)
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(products, many=True)
        return Response(serializer.data)


class ProductReviewViewSet(viewsets.ViewSet):
    """
    ViewSet for product review operations with dependency injection.
    """
    
    def __init__(self, review_service=None, product_service=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency injection with fallback to defaults
        self.review_service = review_service or self._create_default_review_service()
        self.product_service = product_service or self._create_default_product_service()
    
    def _create_default_review_service(self):
        """Factory method for default review service creation."""
        review_repository = ProductReviewRepository()
        return ReviewService(review_repository)
    
    def _create_default_product_service(self):
        """Factory method for default product service creation."""
        product_repository = ProductRepository()
        return ProductService(product_repository)
    
    def list(self, request):
        """GET /reviews/ - List reviews with optional product filtering."""
        product_id = request.query_params.get('product')
        
        if product_id:
            reviews = self.review_service.get_reviews_by_product(product_id)
        else:
            reviews = self.review_service.get_all_reviews()
        
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """GET /reviews/{id}/ - Retrieve single review."""
        try:
            review = self.review_service.get_review_by_id(pk)
            serializer = ProductReviewSerializer(review)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """POST /reviews/ - Create new review with validation."""
        try:
            self.review_service.validate_review(request.data)
            review = self.review_service.create_review(request.data)
            serializer = ProductReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """PUT /reviews/{id}/ - Update review with validation."""
        try:
            self.review_service.validate_review(request.data)
            review = self.review_service.update_review(pk, request.data)
            serializer = ProductReviewSerializer(review)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /reviews/{id}/ - Delete review."""
        try:
            result = self.review_service.delete_review(pk)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Failed to delete review'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)