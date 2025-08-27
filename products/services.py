from .repositories import ProductRepository, CategoryRepository, ProductReviewRepository
from django.core.exceptions import ValidationError


class ProductService:
    """
    Service class for product-related business logic.
    Focuses solely on product business operations.
    """
    
    def __init__(self, product_repository: ProductRepository):
        """
        Initialize service with product repository dependency.
        
        Args:
            product_repository: Repository for product data access
        """
        self.product_repository = product_repository
    
    def get_product_by_id(self, product_id):
        """
        Get product by ID.
        
        Args:
            product_id: ID of the product to retrieve
            
        Returns:
            Product: The product object
            
        Raises:
            ValueError: If product not found
        """
        return self.product_repository.get_by_id(product_id)
    
    def create_product(self, product_data):
        """
        Create a new product.
        
        Args:
            product_data: Dictionary containing product data
            
        Returns:
            Product: The created product object
        """
        return self.product_repository.create(**product_data)
    
    def update_product(self, product_id, product_data):
        """
        Update an existing product.
        
        Args:
            product_id: ID of the product to update
            product_data: Dictionary containing updated product data
            
        Returns:
            Product: The updated product object
            
        Raises:
            ValueError: If product not found
        """
        return self.product_repository.update(product_id, **product_data)
    
    def delete_product(self, product_id):
        """
        Delete a product.
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValueError: If product not found
        """
        return self.product_repository.delete(product_id)
    
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
    
    def get_products_with_filters_and_enrichment(self, filters, category_repository, review_repository):
        """
        Get products with filtering and enrichment.
        This method coordinates with other services for enrichment.
        
        Args:
            filters: dict with category, search, min_price, max_price
            category_repository: Repository for category data access
            review_repository: Repository for review data access
            
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
                category_obj = category_repository.get_by_id(product.category_id)
                product.category_name = category_obj.name
            except ValueError:
                product.category_name = "Unknown Category"
            
            # Image count enrichment (using direct model access for now - can be abstracted later)
            from .models import ProductImage
            images = ProductImage.objects.filter(product=product)
            product.image_count = len(images)
            
            # Average rating enrichment using repository
            reviews = review_repository.get_by_product(product.id)
            if reviews:
                total_rating = 0
                for review in reviews:
                    total_rating += review.rating
                product.average_rating = total_rating / len(reviews)
            else:
                product.average_rating = 0
        
        return queryset
    
    def _get_active_discount_for_product(self, product_id, discount_repository):
        """
        Get active discount for a specific product.
        
        Args:
            product_id: ID of the product
            discount_repository: Repository for discount data access
            
        Returns:
            ProductDiscount or None: The active discount for the product
        """
        from django.utils import timezone
        current_date = timezone.now()
        return discount_repository.get_active_discount_for_product(product_id, current_date)
    
    def _calculate_discounted_price(self, product, discount):
        """
        Calculate discounted price for a product.
        
        Args:
            product: Product object
            discount: ProductDiscount object or None
            
        Returns:
            Decimal: The discounted price (or original price if no discount)
        """
        from decimal import Decimal
        
        if discount is None:
            return product.price
        
        discount_percentage = Decimal(str(discount.discount_percentage))
        discount_amount = product.price * (discount_percentage / 100)
        return product.price - discount_amount
    
    def get_product_with_discount_price(self, product_id, discount_repository):
        """
        Get product with discount price calculation.
        
        Args:
            product_id: ID of the product
            discount_repository: Repository for discount data access
            
        Returns:
            Product: Product with discount information attached
        """
        product = self.get_product_by_id(product_id)
        active_discount = self._get_active_discount_for_product(product_id, discount_repository)
        
        # Add discount information to the product object
        product.discounted_price = self._calculate_discounted_price(product, active_discount)
        product.has_active_discount = active_discount is not None
        product.discount_percentage = active_discount.discount_percentage if active_discount else 0
        
        return product


class CategoryService:
    """
    Service class for category-related business logic.
    Focuses solely on category business operations.
    """
    
    def __init__(self, category_repository: CategoryRepository):
        """
        Initialize service with category repository dependency.
        
        Args:
            category_repository: Repository for category data access
        """
        self.category_repository = category_repository
    
    def get_all_categories(self):
        """
        Get all categories.
        
        Returns:
            QuerySet: All categories
        """
        return self.category_repository.get_all()
    
    def get_category_by_id(self, category_id):
        """
        Get category by ID.
        
        Args:
            category_id: ID of the category to retrieve
            
        Returns:
            Category: The category object
            
        Raises:
            ValueError: If category not found
        """
        return self.category_repository.get_by_id(category_id)
    
    def create_category(self, category_data):
        """
        Create a new category.
        
        Args:
            category_data: Dictionary containing category data
            
        Returns:
            Category: The created category object
        """
        return self.category_repository.create(**category_data)
    
    def update_category(self, category_id, category_data):
        """
        Update an existing category.
        
        Args:
            category_id: ID of the category to update
            category_data: Dictionary containing updated category data
            
        Returns:
            Category: The updated category object
            
        Raises:
            ValueError: If category not found
        """
        return self.category_repository.update(category_id, **category_data)
    
    def delete_category(self, category_id):
        """
        Delete a category.
        
        Args:
            category_id: ID of the category to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValueError: If category not found
        """
        return self.category_repository.delete(category_id)
    
    def validate_category(self, category_data):
        """
        Validate category business rules.
        
        Args:
            category_data: Dictionary containing category data
            
        Raises:
            ValidationError: If business rules are violated
        """
        if not category_data.get('name'):
            raise ValidationError("Category name is required")
        
        if len(category_data.get('name', '').strip()) < 2:
            raise ValidationError("Category name must be at least 2 characters long")


class ReviewService:
    """
    Service class for review-related business logic.
    Focuses solely on review business operations.
    """
    
    def __init__(self, review_repository: ProductReviewRepository):
        """
        Initialize service with review repository dependency.
        
        Args:
            review_repository: Repository for review data access
        """
        self.review_repository = review_repository
    
    def get_all_reviews(self):
        """
        Get all reviews.
        
        Returns:
            QuerySet: All reviews
        """
        return self.review_repository.get_all()
    
    def get_review_by_id(self, review_id):
        """
        Get review by ID.
        
        Args:
            review_id: ID of the review to retrieve
            
        Returns:
            ProductReview: The review object
            
        Raises:
            ValueError: If review not found
        """
        return self.review_repository.get_by_id(review_id)
    
    def create_review(self, review_data):
        """
        Create a new review.
        
        Args:
            review_data: Dictionary containing review data
            
        Returns:
            ProductReview: The created review object
        """
        return self.review_repository.create(**review_data)
    
    def update_review(self, review_id, review_data):
        """
        Update an existing review.
        
        Args:
            review_id: ID of the review to update
            review_data: Dictionary containing updated review data
            
        Returns:
            ProductReview: The updated review object
            
        Raises:
            ValueError: If review not found
        """
        return self.review_repository.update(review_id, **review_data)
    
    def delete_review(self, review_id):
        """
        Delete a review.
        
        Args:
            review_id: ID of the review to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValueError: If review not found
        """
        return self.review_repository.delete(review_id)
    
    def validate_review(self, review_data):
        """
        Validate review business rules.
        
        Args:
            review_data: Dictionary containing review data
            
        Raises:
            ValidationError: If business rules are violated
        """
        rating = review_data.get('rating')
        if rating is not None and (rating < 1 or rating > 5):
            raise ValidationError("Rating must be between 1 and 5")
        
        if not review_data.get('comment'):
            raise ValidationError("Review comment is required")
        
        if len(review_data.get('comment', '').strip()) < 10:
            raise ValidationError("Review comment must be at least 10 characters long")
    
    def get_reviews_by_product(self, product_id):
        """
        Get reviews filtered by product ID.
        
        Args:
            product_id: ID of the product to filter by
            
        Returns:
            QuerySet: Reviews for the specified product
        """
        return self.review_repository.get_by_product(product_id)
