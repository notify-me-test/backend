"""
Tests for product services.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch
from decimal import Decimal
from products.services import ProductService
from products.models import Product
from products.services import CategoryService
from products.services import ReviewService


class ProductServiceTest(TestCase):
    """Test cases for ProductService class using mocking."""
    
    def setUp(self):
        """Set up test data and mocks for each test."""
        # Create mock repository
        self.product_repository = Mock()
        
        # Create service with mock repository
        self.service = ProductService(self.product_repository)
    
    # Stock Update Tests
    
    def test_update_product_stock_success(self):
        """Test successful stock update."""
        # Mock repository response
        mock_updated_product = Mock()
        mock_updated_product.stock_quantity = 50
        self.product_repository.update_stock.return_value = mock_updated_product
        
        result = self.service.update_product_stock(1, 50)
        
        # Verify repository was called correctly
        self.product_repository.update_stock.assert_called_once_with(1, 50)
        
        # Verify result
        self.assertEqual(result['message'], 'Stock updated successfully')
        self.assertEqual(result['new_stock'], 50)
    
    def test_update_product_stock_none_value(self):
        """Test stock update with None value."""
        result = self.service.update_product_stock(1, None)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'stock_quantity is required')
        
        # Verify repository was not called
        self.product_repository.update_stock.assert_not_called()
    
    def test_update_product_stock_invalid_type(self):
        """Test stock update with invalid type."""
        result = self.service.update_product_stock(1, "invalid")
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'stock_quantity must be a number')
        
        # Verify repository was not called
        self.product_repository.update_stock.assert_not_called()
    
    def test_update_product_stock_negative_value(self):
        """Test stock update with negative value."""
        result = self.service.update_product_stock(1, -10)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'stock_quantity cannot be negative')
        
        # Verify repository was not called
        self.product_repository.update_stock.assert_not_called()
    
    def test_update_product_stock_repository_error(self):
        """Test stock update when repository raises error."""
        # Mock repository to raise ValueError
        self.product_repository.update_stock.side_effect = ValueError("Product not found")
        
        result = self.service.update_product_stock(1, 50)
        
        # Verify repository was called
        self.product_repository.update_stock.assert_called_once_with(1, 50)
        
        # Verify error is returned
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Product not found')
    
    # Low Stock Tests
    
    def test_get_low_stock_products_valid_threshold(self):
        """Test getting low stock products with valid threshold."""
        # Mock repository response
        mock_queryset = Mock()
        mock_queryset.count.return_value = 3
        self.product_repository.get_low_stock.return_value = mock_queryset
        
        result = self.service.get_low_stock_products(5)
        
        # Verify repository was called correctly
        self.product_repository.get_low_stock.assert_called_once_with(5)
        
        # Verify result
        self.assertEqual(result, mock_queryset)
    
    def test_get_low_stock_products_invalid_threshold_string(self):
        """Test getting low stock products with invalid string threshold."""
        # Mock repository response
        mock_queryset = Mock()
        self.product_repository.get_low_stock.return_value = mock_queryset
        
        result = self.service.get_low_stock_products("invalid")
        
        # Verify repository was called with default threshold
        self.product_repository.get_low_stock.assert_called_once_with(10)
        
        # Verify result
        self.assertEqual(result, mock_queryset)
    
    def test_get_low_stock_products_invalid_threshold_float(self):
        """Test getting low stock products with invalid float threshold."""
        # Mock repository response
        mock_queryset = Mock()
        self.product_repository.get_low_stock.return_value = mock_queryset
        
        result = self.service.get_low_stock_products(5.5)
        
        # Verify repository was called with converted integer
        self.product_repository.get_low_stock.assert_called_once_with(5)
        
        # Verify result
        self.assertEqual(result, mock_queryset)
    
    # Search Tests
    
    def test_search_products_with_query(self):
        """Test product search with valid query."""
        # Mock repository response
        mock_queryset = Mock()
        mock_queryset.count.return_value = 2
        self.product_repository.search_by_name_or_description.return_value = mock_queryset
        
        result = self.service.search_products("laptop")
        
        # Verify repository was called correctly
        self.product_repository.search_by_name_or_description.assert_called_once_with("laptop")
        
        # Verify result
        self.assertEqual(result, mock_queryset)
    
    def test_search_products_empty_query(self):
        """Test product search with empty query."""
        # Mock repository response
        mock_queryset = Mock()
        mock_queryset.none.return_value = Mock()
        self.product_repository.get_all.return_value = mock_queryset
        
        result = self.service.search_products("")
        
        # Verify repository was called correctly
        self.product_repository.get_all.assert_called_once()
        mock_queryset.none.assert_called_once()
        
        # Verify result is empty queryset
        self.assertEqual(result, mock_queryset.none())
    
    def test_search_products_none_query(self):
        """Test product search with None query."""
        # Mock repository response
        mock_queryset = Mock()
        mock_queryset.none.return_value = Mock()
        self.product_repository.get_all.return_value = mock_queryset
        
        result = self.service.search_products(None)
        
        # Verify repository was called correctly
        self.product_repository.get_all.assert_called_once()
        mock_queryset.none.assert_called_once()
        
        # Verify result is empty queryset
        self.assertEqual(result, mock_queryset.none())


class CategoryServiceTest(TestCase):
    """Test cases for CategoryService class using mocking."""
    
    def setUp(self):
        """Set up test data and mocks for each test."""
        # Create mock repository
        self.category_repository = Mock()
        
        # Create service with mock repository
        self.service = CategoryService(self.category_repository)
    
    # Category Validation Tests
    
    def test_validate_category_valid(self):
        """Test category validation with valid data."""
        category_data = {
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets'
        }
        
        # Should not raise any exception
        self.service.validate_category(category_data)
    
    def test_validate_category_missing_name(self):
        """Test category validation with missing name."""
        category_data = {
            'description': 'Electronic devices and gadgets'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_category(category_data)
        
        self.assertIn("Category name is required", str(context.exception))
    
    def test_validate_category_empty_name(self):
        """Test category validation with empty name."""
        category_data = {
            'name': '',
            'description': 'Electronic devices and gadgets'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_category(category_data)
        
        self.assertIn("Category name is required", str(context.exception))
    
    def test_validate_category_none_name(self):
        """Test category validation with None name."""
        category_data = {
            'name': None,
            'description': 'Electronic devices and gadgets'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_category(category_data)
        
        self.assertIn("Category name is required", str(context.exception))
    
    def test_validate_category_short_name(self):
        """Test category validation with name too short."""
        category_data = {
            'name': 'A',  # Only 1 character
            'description': 'Electronic devices and gadgets'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_category(category_data)
        
        self.assertIn("Category name must be at least 2 characters long", str(context.exception))
    
    def test_validate_category_whitespace_name(self):
        """Test category validation with whitespace-only name."""
        category_data = {
            'name': '   ',  # Only whitespace
            'description': 'Electronic devices and gadgets'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_category(category_data)
        
        self.assertIn("Category name must be at least 2 characters long", str(context.exception))
    
    def test_validate_category_exact_minimum_length(self):
        """Test category validation with exactly minimum length name."""
        category_data = {
            'name': 'AB',  # Exactly 2 characters
            'description': 'Electronic devices and gadgets'
        }
        
        # Should not raise any exception
        self.service.validate_category(category_data)
    

class ReviewServiceTest(TestCase):
    """Test cases for ReviewService class using mocking."""
    
    def setUp(self):
        """Set up test data and mocks for each test."""
        # Create mock repository
        self.review_repository = Mock()
        
        # Create service with mock repository
        self.service = ReviewService(self.review_repository)
    
    # Review Validation Tests
    
    def test_validate_review_valid(self):
        """Test review validation with valid data."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 4,
            'comment': 'This is a great product with excellent quality!'
        }
        
        # Should not raise any exception
        self.service.validate_review(review_data)
    
    def test_validate_review_invalid_rating_too_low(self):
        """Test review validation with rating too low."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 0,  # Below minimum
            'comment': 'This is a great product with excellent quality!'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_review(review_data)
        
        self.assertIn("Rating must be between 1 and 5", str(context.exception))
    
    def test_validate_review_invalid_rating_too_high(self):
        """Test review validation with rating too high."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 6,  # Above maximum
            'comment': 'This is a great product with excellent quality!'
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_review(review_data)
        
        self.assertIn("Rating must be between 1 and 5", str(context.exception))
    
    def test_validate_review_missing_comment(self):
        """Test review validation with missing comment."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 4
            # Missing comment
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_review(review_data)
        
        self.assertIn("Review comment is required", str(context.exception))
    
    def test_validate_review_empty_comment(self):
        """Test review validation with empty comment."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 4,
            'comment': ''
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_review(review_data)
        
        self.assertIn("Review comment is required", str(context.exception))
    
    def test_validate_review_none_comment(self):
        """Test review validation with None comment."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 4,
            'comment': None
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_review(review_data)
        
        self.assertIn("Review comment is required", str(context.exception))
    
    def test_validate_review_short_comment(self):
        """Test review validation with comment too short."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 4,
            'comment': 'Good'  # Only 4 characters, below minimum of 10
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.validate_review(review_data)
        
        self.assertIn("Review comment must be at least 10 characters long", str(context.exception))
    
    def test_validate_review_exact_minimum_comment_length(self):
        """Test review validation with exactly minimum comment length."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'rating': 4,
            'comment': 'Good item!'  # Exactly 10 characters
        }
        
        # Should not raise any exception
        self.service.validate_review(review_data)
    
    def test_validate_review_no_rating(self):
        """Test review validation with no rating (should be valid)."""
        review_data = {
            'product': 1,
            'user_id': 123,
            'comment': 'This is a great product with excellent quality!'
            # No rating field
        }
        
        # Should not raise any exception (rating is optional)
        self.service.validate_review(review_data)
    
    # Review Query Tests
    
    def test_get_reviews_by_product_success(self):
        """Test successful review retrieval by product ID."""
        # Mock repository response
        mock_queryset = Mock()
        mock_queryset.count.return_value = 3
        self.review_repository.get_by_product.return_value = mock_queryset
        
        result = self.service.get_reviews_by_product(1)
        
        # Verify repository was called correctly
        self.review_repository.get_by_product.assert_called_once_with(1)
        
        # Verify result
        self.assertEqual(result, mock_queryset)
    
    def test_get_reviews_by_product_no_reviews(self):
        """Test review retrieval when no reviews exist for product."""
        # Mock repository response (empty queryset)
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0
        self.review_repository.get_by_product.return_value = mock_queryset
        
        result = self.service.get_reviews_by_product(999)
        
        # Verify repository was called correctly
        self.review_repository.get_by_product.assert_called_once_with(999)
        
        # Verify result
        self.assertEqual(result, mock_queryset)
        self.assertEqual(result.count(), 0)


    



