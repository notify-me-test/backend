from .models import Product, Category, ProductImage, ProductReview
from django.db.models import Q


class ProductService:
    """
    Service class for product-related business logic.
    Separates business logic from HTTP concerns in ViewSets.
    """
    
    def update_product_stock(self, product_id, new_stock):
        """
        Update product stock quantity with validation.
        
        Args:
            product_id: ID of the product to update
            new_stock: New stock quantity value
            
        Returns:
            dict: Success message and new stock, or error message
        """
        if new_stock is None:
            return {'error': 'stock_quantity is required'}
        
        try:
            new_stock = int(new_stock)
        except ValueError:
            return {'error': 'stock_quantity must be a number'}
        
        if new_stock < 0:
            return {'error': 'stock_quantity cannot be negative'}
        
        product = Product.objects.get(id=product_id)
        product.stock_quantity = new_stock
        product.save()
        
        return {'message': 'Stock updated successfully', 'new_stock': new_stock}
    
    def get_low_stock_products(self, threshold):
        """
        Get products with stock quantity below or equal to threshold.
        
        Args:
            threshold: Stock quantity threshold (defaults to 10 if invalid)
            
        Returns:
            QuerySet: Filtered products with low stock
        """
        try:
            threshold = int(threshold)
        except ValueError:
            threshold = 10
        
        return Product.objects.filter(stock_quantity__lte=threshold)
    
    def get_products_with_filters_and_enrichment(self, filters):
        """
        Get products with filtering and enrichment.
        
        Args:
            filters: dict with category, search, min_price, max_price
            
        Returns:
            QuerySet: Filtered and enriched products
        """
        queryset = Product.objects.all()
        
        # Apply business logic filters
        category = filters.get('category')
        if category is not None:
            queryset = queryset.filter(category=category)
        
        search = filters.get('search')
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        min_price = filters.get('min_price')
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = filters.get('max_price')
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Apply business logic enrichment
        for product in queryset:
            # Category name enrichment
            category_obj = Category.objects.get(id=product.category_id)
            product.category_name = category_obj.name
            
            # Image count enrichment
            images = ProductImage.objects.filter(product=product)
            product.image_count = len(images)
            
            # Average rating enrichment
            reviews = ProductReview.objects.filter(product=product)
            if reviews:
                total_rating = 0
                for review in reviews:
                    total_rating += review.rating
                product.average_rating = total_rating / len(reviews)
            else:
                product.average_rating = 0
        
        return queryset
    
    def search_products(self, query):
        """
        Search products by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet: Products matching the search query
        """
        if not query:
            return Product.objects.none()
        
        all_products = Product.objects.all()
        matching_products = []
        
        for product in all_products:
            if (query.lower() in product.name.lower() or 
                query.lower() in product.description.lower()):
                matching_products.append(product)
        
        return matching_products
    
    def get_reviews_by_product(self, product_id):
        """
        Get reviews filtered by product ID.
        
        Args:
            product_id: ID of the product to filter by
            
        Returns:
            QuerySet: Reviews for the specified product
        """
        queryset = ProductReview.objects.all()
        if product_id is not None:
            queryset = queryset.filter(product=product_id)
        return queryset
