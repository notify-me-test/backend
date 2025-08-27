"""
Tests for product repositories.
"""
from django.test import TestCase
from django.db import IntegrityError
from decimal import Decimal
from django.contrib.auth.models import User
from products.models import Category, Product, ProductDiscount
from products.repositories import ProductRepository
from products.repositories import CategoryRepository
from products.models import ProductReview
from products.repositories import ProductReviewRepository
from django.utils import timezone
from datetime import timedelta


class ProductRepositoryTest(TestCase):
    """Test cases for ProductRepository class."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Create a test category
        self.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and gadgets"
        )
        
        # Create a test product
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product for testing",
            price=Decimal('99.99'),
            stock_quantity=10,
            category=self.category
        )
        
        # Create repository instance
        self.repository = ProductRepository()
    
    # CRUD Operations Tests
    
    def test_create_product_success(self):
        """Test successful product creation."""
        product_data = {
            'name': 'New Product',
            'description': 'A new test product',
            'price': Decimal('149.99'),
            'stock_quantity': 25,
            'category': self.category
        }
        
        created_product = self.repository.create(**product_data)
        
        self.assertIsInstance(created_product, Product)
        self.assertEqual(created_product.name, 'New Product')
        self.assertEqual(created_product.price, Decimal('149.99'))
        self.assertEqual(created_product.category, self.category)
        self.assertEqual(created_product.stock_quantity, 25)
    
    def test_create_product_error_handling(self):
        """Test error handling during product creation."""
        # Try to create product with invalid data (missing required fields)
        with self.assertRaises(ValueError) as context:
            self.repository.create(name="Invalid Product")
        
        self.assertIn("Error creating product", str(context.exception))
    
    def test_get_by_id_success(self):
        """Test successful product retrieval by ID."""
        retrieved_product = self.repository.get_by_id(self.product.id)
        
        self.assertEqual(retrieved_product.id, self.product.id)
        self.assertEqual(retrieved_product.name, self.product.name)
        self.assertEqual(retrieved_product.price, self.product.price)
    
    def test_get_by_id_not_found(self):
        """Test handling of non-existent product ID."""
        with self.assertRaises(ValueError) as context:
            self.repository.get_by_id(99999)
        
        self.assertIn("Product with id 99999 not found", str(context.exception))
    
    def test_get_by_id_error_handling(self):
        """Test error handling during product retrieval."""
        # This test would require mocking to trigger a general exception
        # For now, we'll test the normal flow and the DoesNotExist case above
        pass
    
    def test_update_product_success(self):
        """Test successful product update."""
        updated_product = self.repository.update(
            self.product.id,
            name="Updated Product Name",
            price=Decimal('129.99'),
            stock_quantity=15
        )
        
        self.assertEqual(updated_product.name, "Updated Product Name")
        self.assertEqual(updated_product.price, Decimal('129.99'))
        self.assertEqual(updated_product.stock_quantity, 15)
        
        # Verify changes persisted in database
        refreshed_product = Product.objects.get(id=self.product.id)
        self.assertEqual(refreshed_product.name, "Updated Product Name")
    
    def test_update_product_not_found(self):
        """Test update of non-existent product."""
        with self.assertRaises(ValueError) as context:
            self.repository.update(99999, name="Updated Name")
        
        self.assertIn("Product with id 99999 not found", str(context.exception))
    
    def test_delete_product_success(self):
        """Test successful product deletion."""
        product_id = self.product.id
        
        # Verify product exists before deletion
        self.assertTrue(Product.objects.filter(id=product_id).exists())
        
        # Delete the product
        result = self.repository.delete(product_id)
        
        # Verify deletion was successful
        self.assertTrue(result)
        self.assertFalse(Product.objects.filter(id=product_id).exists())
    
    def test_delete_product_not_found(self):
        """Test deletion of non-existent product."""
        with self.assertRaises(ValueError) as context:
            self.repository.delete(99999)
        
        self.assertIn("Product with id 99999 not found", str(context.exception))
    
    def test_update_stock_success(self):
        """Test successful stock update."""
        new_stock = 50
        
        updated_product = self.repository.update_stock(self.product.id, new_stock)
        
        self.assertEqual(updated_product.stock_quantity, new_stock)
        
        # Verify change persisted in database
        refreshed_product = Product.objects.get(id=self.product.id)
        self.assertEqual(refreshed_product.stock_quantity, new_stock)
    
    def test_update_stock_not_found(self):
        """Test stock update of non-existent product."""
        with self.assertRaises(ValueError) as context:
            self.repository.update_stock(99999, 100)
        
        self.assertIn("Product with id 99999 not found", str(context.exception))
    
    # Query Operations Tests
    
    def test_get_all_products(self):
        """Test retrieving all products."""
        # Create another product to ensure we have multiple
        Product.objects.create(
            name="Second Product",
            description="Another test product",
            price=Decimal('199.99'),
            stock_quantity=5,
            category=self.category
        )
        
        all_products = self.repository.get_all()
        
        self.assertEqual(all_products.count(), 2)
        self.assertIn(self.product, all_products)
        
    def test_get_by_price_range(self):
        """Test filtering products by price range."""
        # Create products with different prices
        cheap_product = Product.objects.create(
            name="Cheap Product",
            description="An affordable product",
            price=Decimal('19.99'),
            stock_quantity=100,
            category=self.category
        )
        
        expensive_product = Product.objects.create(
            name="Expensive Product",
            description="A luxury product",
            price=Decimal('299.99'),
            stock_quantity=2,
            category=self.category
        )
        
        # Test price range 20-100
        mid_range_products = self.repository.get_by_price_range(20.0, 100.0)
        self.assertEqual(mid_range_products.count(), 1)
        self.assertIn(self.product, mid_range_products)
        
        # Test price range 0-50
        cheap_products = self.repository.get_by_price_range(0.0, 50.0)
        self.assertEqual(cheap_products.count(), 1)
        self.assertIn(cheap_product, cheap_products)
    
    def test_get_low_stock(self):
        """Test filtering products by low stock threshold."""
        # Create products with different stock levels
        low_stock_product = Product.objects.create(
            name="Low Stock Product",
            description="Product with low stock",
            price=Decimal('49.99'),
            stock_quantity=3,
            category=self.category
        )
        
        high_stock_product = Product.objects.create(
            name="High Stock Product",
            description="Product with high stock",
            price=Decimal('79.99'),
            stock_quantity=50,
            category=self.category
        )
        
        # Test threshold of 5 (should include products with stock <= 5)
        low_stock_products = self.repository.get_low_stock(5)
        self.assertEqual(low_stock_products.count(), 1)  # only low_stock_product (3)
        self.assertIn(low_stock_product, low_stock_products)
        self.assertNotIn(self.product, low_stock_products)  # stock=10 is not <= 5
        
        # Test threshold of 2 (should include only products with stock <= 2)
        very_low_stock_products = self.repository.get_low_stock(2)
        self.assertEqual(very_low_stock_products.count(), 0)
      
    def test_search_by_name_or_description(self):
        """Test searching products by name or description."""
        # Create products with searchable names and descriptions
        Product.objects.create(
            name="Gaming Laptop",
            description="High-performance gaming computer",
            price=Decimal('1299.99'),
            stock_quantity=4,
            category=self.category
        )
        
        Product.objects.create(
            name="Office Computer",
            description="Reliable office laptop for work",
            price=Decimal('599.99'),
            stock_quantity=10,
            category=self.category
        )
        
        # Search for "laptop" (should find both by name and description)
        laptop_results = self.repository.search_by_name_or_description("laptop")
        self.assertEqual(laptop_results.count(), 2)
        
        # Search for "gaming" (should find one by description)
        gaming_results = self.repository.search_by_name_or_description("gaming")
        self.assertEqual(gaming_results.count(), 1)
        
        # Search for "office" (should find one by description)
        office_results = self.repository.search_by_name_or_description("office")
        self.assertEqual(office_results.count(), 1)
        
        # Search for non-existent term
        no_results = self.repository.search_by_name_or_description("NonExistent")
        self.assertEqual(no_results.count(), 0)
    
    def test_get_products_with_active_discounts(self):
        """Test retrieving products that have active discounts."""
        now = timezone.now()
        
        # Create another product without discount
        product_without_discount = Product.objects.create(
            name="No Discount Product",
            description="Product without any discount",
            price=Decimal('50.00'),
            stock_quantity=20,
            category=self.category,
            sku="NODISCOUNT123"
        )
        
        # Create active discount for self.product
        active_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(days=5),
            is_active=True
        )
        
        # Create expired discount for product_without_discount
        expired_discount = ProductDiscount.objects.create(
            product=product_without_discount,
            discount_percentage=15.00,
            start_date=now - timedelta(days=10),
            end_date=now - timedelta(days=5),
            is_active=True
        )
        
        # Test method (this will fail until we implement it)
        discounted_products = self.repository.get_products_with_active_discounts(now)
        self.assertEqual(discounted_products.count(), 1)
        self.assertIn(self.product, discounted_products)
        self.assertNotIn(product_without_discount, discounted_products)


class CategoryRepositoryTest(TestCase):
    """Test cases for CategoryRepository class."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Create a test category
        self.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and gadgets"
        )
        
        # Create repository instance
        self.repository = CategoryRepository()
    
    # CRUD Operations Tests
    
    def test_create_category_success(self):
        """Test successful category creation."""
        category_data = {
            'name': 'New Category',
            'description': 'A new test category'
        }
        
        created_category = self.repository.create(**category_data)
        
        self.assertIsInstance(created_category, Category)
        self.assertEqual(created_category.name, 'New Category')
        self.assertEqual(created_category.description, 'A new test category')
    

    def test_get_by_id_success(self):
        """Test successful category retrieval by ID."""
        retrieved_category = self.repository.get_by_id(self.category.id)
        
        self.assertEqual(retrieved_category.id, self.category.id)
        self.assertEqual(retrieved_category.name, self.category.name)
        self.assertEqual(retrieved_category.description, self.category.description)
    
    def test_get_by_id_not_found(self):
        """Test handling of non-existent category ID."""
        with self.assertRaises(ValueError) as context:
            self.repository.get_by_id(99999)
        
        self.assertIn("Category with id 99999 not found", str(context.exception))
    

    
    def test_update_category_success(self):
        """Test successful category update."""
        updated_category = self.repository.update(
            self.category.id,
            name="Updated Electronics",
            description="Updated electronic devices description"
        )
        
        self.assertEqual(updated_category.name, "Updated Electronics")
        self.assertEqual(updated_category.description, "Updated electronic devices description")
        
        # Verify changes persisted in database
        refreshed_category = Category.objects.get(id=self.category.id)
        self.assertEqual(refreshed_category.name, "Updated Electronics")
    
    def test_update_category_not_found(self):
        """Test update of non-existent category."""
        with self.assertRaises(ValueError) as context:
            self.repository.update(99999, name="Updated Name")
        
        self.assertIn("Category with id 99999 not found", str(context.exception))
    
    def test_delete_category_success(self):
        """Test successful category deletion."""
        category_id = self.category.id
        
        # Verify category exists before deletion
        self.assertTrue(Category.objects.filter(id=category_id).exists())
        
        # Delete the category
        result = self.repository.delete(category_id)
        
        # Verify deletion was successful
        self.assertTrue(result)
        self.assertFalse(Category.objects.filter(id=category_id).exists())
    
    def test_delete_category_not_found(self):
        """Test deletion of non-existent category."""
        with self.assertRaises(ValueError) as context:
            self.repository.delete(99999)
        
        self.assertIn("Category with id 99999 not found", str(context.exception))
    
    # Query Operations Tests
    
    def test_get_all_categories(self):
        """Test retrieving all categories."""
        # Create another category to ensure we have multiple
        Category.objects.create(
            name="Clothing",
            description="Clothing and fashion items"
        )
        
        all_categories = self.repository.get_all()
        
        self.assertEqual(all_categories.count(), 2)
        self.assertIn(self.category, all_categories)


class ProductReviewRepositoryTest(TestCase):
    """Test cases for ProductReviewRepository class."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Create test categories and products
        self.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and gadgets"
        )
        
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product for testing",
            price=Decimal('99.99'),
            stock_quantity=10,
            category=self.category
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a test review
        self.review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment="Great product, highly recommended!"
        )
        
        # Create repository instance
        self.repository = ProductReviewRepository()
    
    # CRUD Operations Tests
    
    def test_create_review_success(self):
        """Test successful review creation."""
        # Create another user for this test
        another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpass123'
        )
        
        review_data = {
            'product': self.product,
            'user': another_user,
            'rating': 5,
            'comment': 'Excellent product!'
        }
        
        created_review = self.repository.create(**review_data)
        
        self.assertIsInstance(created_review, ProductReview)
        self.assertEqual(created_review.product, self.product)
        self.assertEqual(created_review.user, another_user)
        self.assertEqual(created_review.rating, 5)
        self.assertEqual(created_review.comment, 'Excellent product!')
    
    def test_create_review_error_handling(self):
        """Test error handling during review creation."""
        # Try to create review with invalid data (missing required fields)
        with self.assertRaises(ValueError) as context:
            self.repository.create(comment="Invalid Review")
        
        self.assertIn("Error creating review", str(context.exception))
    
    def test_get_by_id_success(self):
        """Test successful review retrieval by ID."""
        retrieved_review = self.repository.get_by_id(self.review.id)
        
        self.assertEqual(retrieved_review.id, self.review.id)
        self.assertEqual(retrieved_review.product, self.review.product)
        self.assertEqual(retrieved_review.user, self.review.user)
        self.assertEqual(retrieved_review.rating, self.review.rating)
        self.assertEqual(retrieved_review.comment, self.review.comment)
    
    def test_get_by_id_not_found(self):
        """Test handling of non-existent review ID."""
        with self.assertRaises(ValueError) as context:
            self.repository.get_by_id(99999)
        
        self.assertIn("Review with id 99999 not found", str(context.exception))
    
    def test_update_review_success(self):
        """Test successful review update."""
        updated_review = self.repository.update(
            self.review.id,
            rating=5,
            comment="Updated comment - even better than before!"
        )
        
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(updated_review.comment, "Updated comment - even better than before!")
        
        # Verify changes persisted in database
        refreshed_review = ProductReview.objects.get(id=self.review.id)
        self.assertEqual(refreshed_review.rating, 5)
        self.assertEqual(refreshed_review.comment, "Updated comment - even better than before!")
    
    def test_update_review_not_found(self):
        """Test update of non-existent review."""
        with self.assertRaises(ValueError) as context:
            self.repository.update(99999, rating=5)
        
        self.assertIn("Review with id 99999 not found", str(context.exception))
    
    def test_delete_review_success(self):
        """Test successful review deletion."""
        review_id = self.review.id
        
        # Verify review exists before deletion
        self.assertTrue(ProductReview.objects.filter(id=review_id).exists())
        
        # Delete the review
        result = self.repository.delete(review_id)
        
        # Verify deletion was successful
        self.assertTrue(result)
        self.assertFalse(ProductReview.objects.filter(id=review_id).exists())
    
    def test_delete_review_not_found(self):
        """Test deletion of non-existent review."""
        with self.assertRaises(ValueError) as context:
            self.repository.delete(99999)
        
        self.assertIn("Review with id 99999 not found", str(context.exception))
    
    # Query Operations Tests
    
    def test_get_all_reviews(self):
        """Test retrieving all reviews."""
        # Create another review to ensure we have multiple
        another_user = User.objects.create_user(
            username='thirduser',
            email='third@example.com',
            password='testpass123'
        )
        ProductReview.objects.create(
            product=self.product,
            user=another_user,
            rating=3,
            comment="Decent product"
        )
        
        all_reviews = self.repository.get_all()
        
        self.assertEqual(all_reviews.count(), 2)
        self.assertIn(self.review, all_reviews)
    
    def test_get_by_product(self):
        """Test filtering reviews by product ID."""
        # Create another product and review
        second_product = Product.objects.create(
            name="Second Product",
            description="Another test product",
            price=Decimal('149.99'),
            stock_quantity=5,
            category=self.category
        )
        
        second_review = ProductReview.objects.create(
            product=second_product,
            user=self.user,  # Use the existing user from setUp
            rating=4,
            comment="Good second product"
        )
        
        # Get reviews for the first product
        first_product_reviews = self.repository.get_by_product(self.product.id)
        self.assertEqual(first_product_reviews.count(), 1)
        self.assertIn(self.review, first_product_reviews)
        
        # Get reviews for the second product
        second_product_reviews = self.repository.get_by_product(second_product.id)
        self.assertEqual(second_product_reviews.count(), 1)
        self.assertIn(second_review, second_product_reviews)
    

