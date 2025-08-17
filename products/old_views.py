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

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if category is not None:
            queryset = queryset.filter(category=category)
        
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        for product in queryset:
            category_obj = Category.objects.get(id=product.category_id)
            product.category_name = category_obj.name
            
            images = ProductImage.objects.filter(product=product)
            product.image_count = len(images)
            
            reviews = ProductReview.objects.filter(product=product)
            if reviews:
                total_rating = 0
                for review in reviews:
                    total_rating += review.rating
                product.average_rating = total_rating / len(reviews)
            else:
                product.average_rating = 0
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        product = self.get_object()
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
        
        product.stock_quantity = new_stock
        product.save()
        
        return Response({'message': 'Stock updated successfully', 
                        'new_stock': new_stock})
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        threshold = request.query_params.get('threshold', 10)
        try:
            threshold = int(threshold)
        except ValueError:
            threshold = 10
        
        products = Product.objects.filter(stock_quantity__lte=threshold)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    
    def get_queryset(self):
        queryset = ProductReview.objects.all()
        product_id = self.request.query_params.get('product', None)
        if product_id is not None:
            queryset = queryset.filter(product=product_id)
        return queryset

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        
        if not query:
            return Product.objects.none()
        
        all_products = Product.objects.all()
        matching_products = []
        
        for product in all_products:
            if (query.lower() in product.name.lower() or 
                query.lower() in product.description.lower()):
                matching_products.append(product)
        
        return matching_products