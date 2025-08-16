from .repositories import ProductRepository, CategoryRepository, ProductReviewRepository


class ProductService:
    """
    Service class for product-related business logic.
    Separates business logic from HTTP concerns in ViewSets.
    Uses repositories for data access to follow SOLID principles.
    """
    
    def __init__(self, product_repository: ProductRepository, 
                 category_repository: CategoryRepository,
                 review_repository: ProductReviewRepository):
        """
        Initialize service with repository dependencies.
        
        Args:
            product_repository: Repository for product data access
            category_repository: Repository for category data access
            review_repository: Repository for review data access
        """
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.review_repository = review_repository
    
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
        
        try:
            product = self.product_repository.update_stock(product_id, new_stock)
            return {'message': 'Stock updated successfully', 'new_stock': new_stock}
        except ValueError as e:
            return {'error': str(e)}
    
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
        
        return self.product_repository.get_low_stock(threshold)
    
    def get_products_with_filters_and_enrichment(self, filters):
        """
        Get products with filtering and enrichment.
        
        Args:
            filters: dict with category, search, min_price, max_price
            
        Returns:
            QuerySet: Filtered and enriched products
        """
        # Start with all products
        queryset = self.product_repository.get_all()
        
        # Apply business logic filters using repositories
        category = filters.get('category')
        if category is not None:
            queryset = queryset.filter(category=category)
        
        search = filters.get('search')
        if search is not None:
            queryset = self.product_repository.search_by_name_or_description(search)
        
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        if min_price is not None or max_price is not None:
            min_price = min_price if min_price is not None else 0
            max_price = max_price if max_price is not None else float('inf')
            queryset = self.product_repository.get_by_price_range(min_price, max_price)
        
        # Apply business logic enrichment using repositories
        for product in queryset:
            # Category name enrichment
            try:
                category_obj = self.category_repository.get_by_id(product.category_id)
                product.category_name = category_obj.name
            except ValueError:
                product.category_name = "Unknown Category"
            
            # Image count enrichment (using direct model access for now - can be abstracted later)
            from .models import ProductImage
            images = ProductImage.objects.filter(product=product)
            product.image_count = len(images)
            
            # Average rating enrichment using repository
            reviews = self.review_repository.get_by_product(product.id)
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
            return self.product_repository.get_all().none()
        
        return self.product_repository.search_by_name_or_description(query)
    
    def get_reviews_by_product(self, product_id):
        """
        Get reviews filtered by product ID.
        
        Args:
            product_id: ID of the product to filter by
            
        Returns:
            QuerySet: Reviews for the specified product
        """
        return self.review_repository.get_by_product(product_id)
