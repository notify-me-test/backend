"""
Tests for product views.
"""
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from decimal import Decimal
from products.models import Category, Product, ProductReview
from django.contrib.auth.models import User
from products.views import CategoryViewSet
from products.views import ProductViewSet
from products.views import ProductReviewViewSet


class CategoryViewSetTest(TestCase):
    """Test cases for CategoryViewSet class with dependency injection."""
    
    def setUp(self):
        """Set up test data and mocked services for each test."""
        # Create test data for mocking
        self.category_data = {
            'id': 1,
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets'
        }
        
        self.category = Category(**self.category_data)
        
        # Mock data for list operations
        self.categories_list = [
            Category(id=1, name='Electronics', description='Electronic devices'),
            Category(id=2, name='Books', description='Books and literature')
        ]
        
        # Create mocked service
        self.mock_category_service = MagicMock()
        
        # Create ViewSet with injected service
        self.viewset = CategoryViewSet(category_service=self.mock_category_service)
        
        # Create request factory for testing ViewSet methods directly
        self.factory = APIRequestFactory()
        
        # Set up test client for HTTP-level testing
        self.client = APIClient()
    
    # LIST Tests (GET /categories/)
    
    def test_list_categories_success(self):
        """Test successful retrieval of all categories."""
        # Setup mock
        self.mock_category_service.get_all_categories.return_value = self.categories_list
        
        # Create request
        request = self.factory.get('/categories/')
        
        # Call ViewSet method directly
        response = self.viewset.list(request)
        
        # Assert service was called
        self.mock_category_service.get_all_categories.assert_called_once()
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Electronics')
        self.assertEqual(response.data[1]['name'], 'Books')
    
    # RETRIEVE Tests (GET /categories/{id}/)
    
    def test_retrieve_category_success(self):
        """Test successful retrieval of single category."""
        # Setup mock
        self.mock_category_service.get_category_by_id.return_value = self.category
        
        # Create request
        request = self.factory.get('/categories/1/')
        
        # Call ViewSet method directly
        response = self.viewset.retrieve(request, pk='1')
        
        # Assert service was called with correct ID
        self.mock_category_service.get_category_by_id.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')
        self.assertEqual(response.data['description'], 'Electronic devices and gadgets')
    
    def test_retrieve_category_not_found(self):
        """Test handling of non-existent category ID."""
        # Setup mock to raise ValueError
        self.mock_category_service.get_category_by_id.side_effect = ValueError("Category with id 999 not found")
        
        # Create request
        request = self.factory.get('/categories/999/')
        
        # Call ViewSet method directly
        response = self.viewset.retrieve(request, pk='999')
        
        # Assert service was called
        self.mock_category_service.get_category_by_id.assert_called_once_with('999')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Category with id 999 not found', response.data['error'])
    
    # CREATE Tests (POST /categories/)
    
    def test_create_category_success(self):
        """Test successful category creation."""
        # Setup mocks
        self.mock_category_service.validate_category.return_value = None  # No validation errors
        self.mock_category_service.create_category.return_value = self.category
        
        # Request data
        create_data = {
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets'
        }
        
        # Create request
        request = self.factory.post('/categories/', create_data, format='json')
        request.data = create_data  # Add .data attribute for DRF compatibility
        
        # Call ViewSet method directly
        response = self.viewset.create(request)
        
        # Assert services were called with correct data
        self.mock_category_service.validate_category.assert_called_once_with(create_data)
        self.mock_category_service.create_category.assert_called_once_with(create_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Electronics')
        self.assertEqual(response.data['description'], 'Electronic devices and gadgets')
    
    def test_create_category_validation_error(self):
        """Test category creation with validation errors."""
        # Setup mock to raise ValidationError
        self.mock_category_service.validate_category.side_effect = ValidationError("Name is required")
        
        # Request data (missing required field)
        create_data = {
            'description': 'Electronic devices and gadgets'
        }
        
        # Create request
        request = self.factory.post('/categories/', create_data, format='json')
        request.data = create_data  # Add .data attribute for DRF compatibility
        
        # Call ViewSet method directly
        response = self.viewset.create(request)
        
        # Assert validation service was called
        self.mock_category_service.validate_category.assert_called_once_with(create_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Name is required', response.data['error'])
    
    # UPDATE Tests (PUT /categories/{id}/)
    
    def test_update_category_success(self):
        """Test successful category update."""
        # Setup mocks
        self.mock_category_service.validate_category.return_value = None  # No validation errors
        updated_category = Category(id=1, name='Updated Electronics', description='Updated description')
        self.mock_category_service.update_category.return_value = updated_category
        
        # Request data
        update_data = {
            'name': 'Updated Electronics',
            'description': 'Updated description'
        }
        
        # Create request
        request = self.factory.put('/categories/1/', update_data, format='json')
        request.data = update_data  # Add .data attribute for DRF compatibility
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='1')
        
        # Assert services were called with correct parameters
        self.mock_category_service.validate_category.assert_called_once_with(update_data)
        self.mock_category_service.update_category.assert_called_once_with('1', update_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Electronics')
        self.assertEqual(response.data['description'], 'Updated description')
    
    def test_update_category_not_found(self):
        """Test update of non-existent category."""
        # Setup mocks
        self.mock_category_service.validate_category.return_value = None  # No validation errors
        self.mock_category_service.update_category.side_effect = ValueError("Category with id 999 not found")
        
        # Request data
        update_data = {
            'name': 'Updated Electronics',
            'description': 'Updated description'
        }
        
        # Create request
        request = self.factory.put('/categories/999/', update_data, format='json')
        request.data = update_data  # Add .data attribute for DRF compatibility
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='999')
        
        # Assert services were called
        self.mock_category_service.validate_category.assert_called_once_with(update_data)
        self.mock_category_service.update_category.assert_called_once_with('999', update_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Category with id 999 not found', response.data['error'])
    
    def test_update_category_validation_error(self):
        """Test category update with validation errors."""
        # Setup mock to raise ValidationError
        self.mock_category_service.validate_category.side_effect = ValidationError("Name cannot be empty")
        
        # Request data (invalid data)
        update_data = {
            'name': '',  # Empty name should fail validation
            'description': 'Updated description'
        }
        
        # Create request
        request = self.factory.put('/categories/1/', update_data, format='json')
        request.data = update_data  # Add .data attribute for DRF compatibility
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='1')
        
        # Assert validation service was called
        self.mock_category_service.validate_category.assert_called_once_with(update_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Name cannot be empty', response.data['error'])
    
    # DELETE Tests (DELETE /categories/{id}/)
    
    def test_delete_category_success(self):
        """Test successful category deletion."""
        # Setup mock
        self.mock_category_service.delete_category.return_value = True
        
        # Create request
        request = self.factory.delete('/categories/1/')
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='1')
        
        # Assert service was called with correct ID
        self.mock_category_service.delete_category.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_category_not_found(self):
        """Test deletion of non-existent category."""
        # Setup mock to raise ValueError
        self.mock_category_service.delete_category.side_effect = ValueError("Category with id 999 not found")
        
        # Create request
        request = self.factory.delete('/categories/999/')
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='999')
        
        # Assert service was called
        self.mock_category_service.delete_category.assert_called_once_with('999')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Category with id 999 not found', response.data['error'])
    
    def test_delete_category_failure(self):
        """Test category deletion when service returns False."""
        # Setup mock to return False (deletion failed)
        self.mock_category_service.delete_category.return_value = False
        
        # Create request
        request = self.factory.delete('/categories/1/')
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='1')
        
        # Assert service was called
        self.mock_category_service.delete_category.assert_called_once_with('1')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Failed to delete category', response.data['error'])
    
    # Dependency Injection Tests
    
    def test_default_service_creation(self):
        """Test that ViewSet creates default service when none provided."""
        # Create ViewSet without injecting service
        viewset = CategoryViewSet()
        
        # Verify default service was created
        self.assertIsNotNone(viewset.category_service)
        # In production, this should be a real CategoryService instance
        from products.services import CategoryService
        self.assertIsInstance(viewset.category_service, CategoryService)
    
    def test_injected_service_usage(self):
        """Test that injected service is used instead of default."""
        # Create ViewSet with injected service
        viewset = CategoryViewSet(category_service=self.mock_category_service)
        
        # Verify injected service is used
        self.assertEqual(viewset.category_service, self.mock_category_service)


class ProductViewSetTest(TestCase):
    """Test cases for ProductViewSet class with dependency injection."""
    
    def setUp(self):
        """Set up test data and mocked services for each test."""
        # Create test data for mocking
        self.category_data = {
            'id': 1,
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets'
        }
        
        self.category = Category(**self.category_data)
        
        self.product_data = {
            'id': 1,
            'name': 'Test Product',
            'description': 'A test product for testing',
            'price': Decimal('99.99'),
            'stock_quantity': 10,
            'category': self.category
        }
        
        self.product = Product(**self.product_data)
        
        # Mock data for list operations
        self.products_list = [
            Product(id=1, name='Product 1', description='First product', price=Decimal('99.99'), stock_quantity=10, category=self.category),
            Product(id=2, name='Product 2', description='Second product', price=Decimal('149.99'), stock_quantity=5, category=self.category)
        ]
        
        # Create mocked services
        self.mock_product_service = MagicMock()
        self.mock_category_service = MagicMock()
        self.mock_review_service = MagicMock()
        
        # Create ViewSet with injected services
        self.viewset = ProductViewSet(
            product_service=self.mock_product_service,
            category_service=self.mock_category_service,
            review_service=self.mock_review_service
        )
        
        # Create request factory for testing ViewSet methods directly
        self.factory = APIRequestFactory()
        
        # Set up test client for HTTP-level testing
        self.client = APIClient()
    
    # LIST Tests (GET /products/)
    
    def test_list_products_success(self):
        """Test successful retrieval of all products."""
        # Setup mock
        self.mock_product_service.get_products_with_filters_and_enrichment.return_value = self.products_list
        
        # Create request with query parameters
        request = self.factory.get('/products/?category=1&min_price=50&max_price=200')
        
        # Mock request.data and query_params for the test
        request.data = {}
        request.query_params = {'category': '1', 'min_price': '50', 'max_price': '200'}
        
        # Call ViewSet method directly
        response = self.viewset.list(request)
        
        # Assert service was called with correct filters
        self.mock_product_service.get_products_with_filters_and_enrichment.assert_called_once()
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['name'], 'Product 1')
        self.assertEqual(response.data['results'][1]['name'], 'Product 2')
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
    
    # RETRIEVE Tests (GET /products/{id}/)
    
    def test_retrieve_product_success(self):
        """Test successful retrieval of single product."""
        # Setup mock
        self.mock_product_service.get_product_by_id.return_value = self.product
        
        # Create request
        request = self.factory.get('/products/1/')
        
        # Mock request.data for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.retrieve(request, pk='1')
        
        # Assert service was called with correct ID
        self.mock_product_service.get_product_by_id.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['price'], '99.99')
    
    def test_retrieve_product_not_found(self):
        """Test handling of non-existent product ID."""
        # Setup mock to raise ValueError
        self.mock_product_service.get_product_by_id.side_effect = ValueError("Product with id 999 not found")
        
        # Create request
        request = self.factory.get('/products/999/')
        
        # Mock request.data for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.retrieve(request, pk='999')
        
        # Assert service was called
        self.mock_product_service.get_product_by_id.assert_called_once_with('999')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Product with id 999 not found', response.data['error'])
    
    # CREATE Tests (POST /products/)
    
    def test_create_product_success(self):
        """Test successful product creation."""
        # Setup mock
        self.mock_product_service.create_product.return_value = self.product
        
        # Request data
        create_data = {
            'name': 'Test Product',
            'description': 'A test product for testing',
            'price': '99.99',
            'stock_quantity': 10,
            'category': 1
        }
        
        # Create request
        request = self.factory.post('/products/', create_data, format='json')
        
        # Mock request.data for the test
        request.data = create_data
        
        # Call ViewSet method directly
        response = self.viewset.create(request)
        
        # Assert service was called with correct data
        self.mock_product_service.create_product.assert_called_once_with(create_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['price'], '99.99')
    
    def test_create_product_validation_error(self):
        """Test product creation with validation errors."""
        # Setup mock to raise ValidationError
        self.mock_product_service.create_product.side_effect = ValidationError("Name is required")
        
        # Request data (missing required field)
        create_data = {
            'description': 'A test product for testing',
            'price': '99.99'
        }
        
        # Create request
        request = self.factory.post('/products/', create_data, format='json')
        
        # Mock request.data for the test
        request.data = create_data
        
        # Call ViewSet method directly
        response = self.viewset.create(request)
        
        # Assert service was called
        self.mock_product_service.create_product.assert_called_once_with(create_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Name is required', response.data['error'])
    
    # UPDATE Tests (PUT /products/{id}/)
    
    def test_update_product_success(self):
        """Test successful product update."""
        # Setup mock
        updated_product = Product(id=1, name='Updated Product', description='Updated description', price=Decimal('129.99'), stock_quantity=15, category=self.category)
        self.mock_product_service.update_product.return_value = updated_product
        
        # Request data
        update_data = {
            'name': 'Updated Product',
            'description': 'Updated description',
            'price': '129.99',
            'stock_quantity': 15
        }
        
        # Create request
        request = self.factory.put('/products/1/', update_data, format='json')
        
        # Mock request.data for the test
        request.data = update_data
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='1')
        
        # Assert service was called with correct parameters
        self.mock_product_service.update_product.assert_called_once_with('1', update_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Product')
        self.assertEqual(response.data['price'], '129.99')
    
    def test_update_product_not_found(self):
        """Test update of non-existent product."""
        # Setup mock to raise ValueError
        self.mock_product_service.update_product.side_effect = ValueError("Product with id 999 not found")
        
        # Request data
        update_data = {
            'name': 'Updated Product',
            'description': 'Updated description'
        }
        
        # Create request
        request = self.factory.put('/products/999/', update_data, format='json')
        
        # Mock request.data for the test
        request.data = update_data
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='999')
        
        # Assert service was called
        self.mock_product_service.update_product.assert_called_once_with('999', update_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Product with id 999 not found', response.data['error'])
    
    def test_update_product_validation_error(self):
        """Test product update with validation errors."""
        # Setup mock to raise ValidationError
        self.mock_product_service.update_product.side_effect = ValidationError("Price cannot be negative")
        
        # Request data (invalid data)
        update_data = {
            'name': 'Updated Product',
            'price': '-10.00'  # Negative price should fail validation
        }
        
        # Create request
        request = self.factory.put('/products/1/', update_data, format='json')
        
        # Mock request.data for the test
        request.data = update_data
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='1')
        
        # Assert service was called
        self.mock_product_service.update_product.assert_called_once_with('1', update_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Price cannot be negative', response.data['error'])
    
    # DELETE Tests (DELETE /products/{id}/)
    
    def test_delete_product_success(self):
        """Test successful product deletion."""
        # Setup mock
        self.mock_product_service.delete_product.return_value = True
        
        # Create request
        request = self.factory.delete('/products/1/')
        
        # Mock request.data for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='1')
        
        # Assert service was called with correct ID
        self.mock_product_service.delete_product.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_product_not_found(self):
        """Test deletion of non-existent product."""
        # Setup mock to raise ValueError
        self.mock_product_service.delete_product.side_effect = ValueError("Product with id 999 not found")
        
        # Create request
        request = self.factory.delete('/products/999/')
        
        # Mock request.data for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='999')
        
        # Assert service was called
        self.mock_product_service.delete_product.assert_called_once_with('999')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Product with id 999 not found', response.data['error'])
    
    def test_delete_product_failure(self):
        """Test product deletion when service returns False."""
        # Setup mock to return False (deletion failed)
        self.mock_product_service.delete_product.return_value = False
        
        # Create request
        request = self.factory.delete('/products/1/')
        
        # Mock request.data for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='1')
        
        # Assert service was called
        self.mock_product_service.delete_product.assert_called_once_with('1')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Failed to delete product', response.data['error'])
    
    # CUSTOM ACTION Tests
    
    def test_update_stock_success(self):
        """Test successful stock update via custom action."""
        # Setup mock
        updated_product = Product(id=1, name='Test Product', description='A test product', price=Decimal('99.99'), stock_quantity=50, category=self.category)
        self.mock_product_service.update_product_stock.return_value = {'success': True, 'product': updated_product}
        
        # Request data
        stock_data = {'stock_quantity': 50}
        
        # Create request
        request = self.factory.post('/products/1/update_stock/', stock_data, format='json')
        
        # Mock request.data for the test
        request.data = stock_data
        
        # Call ViewSet method directly
        response = self.viewset.update_stock(request, pk='1')
        
        # Assert service was called with correct parameters
        self.mock_product_service.update_product_stock.assert_called_once_with('1', 50)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
    
    def test_update_stock_missing_quantity(self):
        """Test stock update with missing stock_quantity."""
        # Create request without stock_quantity
        request = self.factory.post('/products/1/update_stock/', {}, format='json')
        
        # Mock request.data for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.update_stock(request, pk='1')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('stock_quantity is required', response.data['error'])
    
    def test_update_stock_invalid_quantity(self):
        """Test stock update with invalid stock_quantity."""
        # Create request with invalid stock_quantity
        request = self.factory.post('/products/1/update_stock/', {'stock_quantity': 'invalid'}, format='json')
        
        # Mock request.data for the test
        request.data = {'stock_quantity': 'invalid'}
        
        # Call ViewSet method directly
        response = self.viewset.update_stock(request, pk='1')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('stock_quantity must be a number', response.data['error'])
    
    def test_update_stock_negative_quantity(self):
        """Test stock update with negative stock_quantity."""
        # Create request with negative stock_quantity
        request = self.factory.post('/products/1/update_stock/', {'stock_quantity': -10}, format='json')
        
        # Mock request.data for the test
        request.data = {'stock_quantity': -10}
        
        # Call ViewSet method directly
        response = self.viewset.update_stock(request, pk='1')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('stock_quantity cannot be negative', response.data['error'])
    
    # Dependency Injection Tests
    
    def test_default_service_creation(self):
        """Test that ViewSet creates default services when none provided."""
        # Create ViewSet without injecting services
        viewset = ProductViewSet()
        
        # Verify default services were created
        self.assertIsNotNone(viewset.product_service)
        self.assertIsNotNone(viewset.category_service)
        self.assertIsNotNone(viewset.review_service)
        
        # In production, these should be real service instances
        from products.services import ProductService, CategoryService, ReviewService
        self.assertIsInstance(viewset.product_service, ProductService)
        self.assertIsInstance(viewset.category_service, CategoryService)
        self.assertIsInstance(viewset.review_service, ReviewService)
    
    def test_injected_service_usage(self):
        """Test that injected services are used instead of defaults."""
        # Create ViewSet with injected services
        viewset = ProductViewSet(
            product_service=self.mock_product_service,
            category_service=self.mock_category_service,
            review_service=self.mock_review_service
        )
        
        # Verify injected services are used
        self.assertEqual(viewset.product_service, self.mock_product_service)
        self.assertEqual(viewset.category_service, self.mock_category_service)
        self.assertEqual(viewset.review_service, self.mock_review_service)


class ProductReviewViewSetTest(TestCase):
    """Test cases for ProductReviewViewSet class with dependency injection."""
    
    def setUp(self):
        """Set up test data and mocked services for each test."""
        # Create test data for mocking
        self.user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        self.user = User(**self.user_data)
        
        self.category_data = {
            'id': 1,
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets'
        }
        
        self.category = Category(**self.category_data)
        
        self.product_data = {
            'id': 1,
            'name': 'Test Product',
            'description': 'A test product for testing',
            'price': Decimal('99.99'),
            'stock_quantity': 10,
            'category': self.category
        }
        
        self.product = Product(**self.product_data)
        
        self.review_data = {
            'id': 1,
            'product': self.product,
            'user': self.user,
            'rating': 5,
            'comment': 'Great product!',
            'created_at': '2024-01-15T10:00:00Z'
        }
        
        self.review = ProductReview(**self.review_data)
        
        # Mock data for list operations
        self.reviews_list = [
            ProductReview(id=1, product=self.product, user=self.user, rating=5, comment='Great product!'),
            ProductReview(id=2, product=self.product, user=self.user, rating=4, comment='Good product!')
        ]
        
        # Create mocked services
        self.mock_review_service = MagicMock()
        self.mock_product_service = MagicMock()
        
        # Create ViewSet with injected services
        self.viewset = ProductReviewViewSet(
            review_service=self.mock_review_service,
            product_service=self.mock_product_service
        )
        
        # Create request factory for testing ViewSet methods directly
        self.factory = APIRequestFactory()
        
        # Set up test client for HTTP-level testing
        self.client = APIClient()
    
    # LIST Tests (GET /reviews/)
    
    def test_list_reviews_success(self):
        """Test successful retrieval of all reviews."""
        # Setup mock
        self.mock_review_service.get_all_reviews.return_value = self.reviews_list
        
        # Create request
        request = self.factory.get('/reviews/')
        
        # Mock request attributes for the test
        request.data = {}
        request.query_params = {}
        
        # Call ViewSet method directly
        response = self.viewset.list(request)
        
        # Assert service was called
        self.mock_review_service.get_all_reviews.assert_called_once()
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['rating'], 5)
        self.assertEqual(response.data[1]['rating'], 4)
    
    def test_list_reviews_by_product(self):
        """Test successful retrieval of reviews filtered by product."""
        # Setup mock
        self.mock_review_service.get_reviews_by_product.return_value = self.reviews_list
        
        # Create request with product filter
        request = self.factory.get('/reviews/?product=1')
        
        # Mock request attributes for the test
        request.data = {}
        request.query_params = {'product': '1'}
        
        # Call ViewSet method directly
        response = self.viewset.list(request)
        
        # Assert service was called with correct product ID
        self.mock_review_service.get_reviews_by_product.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    # RETRIEVE Tests (GET /reviews/{id}/)
    
    def test_retrieve_review_success(self):
        """Test successful retrieval of single review."""
        # Setup mock
        self.mock_review_service.get_review_by_id.return_value = self.review
        
        # Create request
        request = self.factory.get('/reviews/1/')
        
        # Mock request attributes for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.retrieve(request, pk='1')
        
        # Assert service was called with correct ID
        self.mock_review_service.get_review_by_id.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great product!')
    
    def test_retrieve_review_not_found(self):
        """Test handling of non-existent review ID."""
        # Setup mock to raise ValueError
        self.mock_review_service.get_review_by_id.side_effect = ValueError("Review with id 999 not found")
        
        # Create request
        request = self.factory.get('/reviews/999/')
        
        # Mock request attributes for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.retrieve(request, pk='999')
        
        # Assert service was called
        self.mock_review_service.get_review_by_id.assert_called_once_with('999')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Review with id 999 not found', response.data['error'])
    
    # CREATE Tests (POST /reviews/)
    
    def test_create_review_success(self):
        """Test successful review creation."""
        # Setup mocks
        self.mock_review_service.validate_review.return_value = None  # No validation errors
        self.mock_review_service.create_review.return_value = self.review
        
        # Request data
        create_data = {
            'product': 1,
            'rating': 5,
            'comment': 'Great product!'
        }
        
        # Create request
        request = self.factory.post('/reviews/', create_data, format='json')
        
        # Mock request attributes for the test
        request.data = create_data
        
        # Call ViewSet method directly
        response = self.viewset.create(request)
        
        # Assert services were called with correct data
        self.mock_review_service.validate_review.assert_called_once_with(create_data)
        self.mock_review_service.create_review.assert_called_once_with(create_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great product!')
    
    def test_create_review_validation_error(self):
        """Test review creation with validation errors."""
        # Setup mock to raise ValidationError
        self.mock_review_service.validate_review.side_effect = ValidationError("Rating must be between 1 and 5")
        
        # Request data (invalid data)
        create_data = {
            'product': 1,
            'rating': 6,  # Invalid rating
            'comment': 'Great product!'
        }
        
        # Create request
        request = self.factory.post('/reviews/', create_data, format='json')
        
        # Mock request attributes for the test
        request.data = create_data
        
        # Call ViewSet method directly
        response = self.viewset.create(request)
        
        # Assert validation service was called
        self.mock_review_service.validate_review.assert_called_once_with(create_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Rating must be between 1 and 5', response.data['error'])
    
    # UPDATE Tests (PUT /reviews/{id}/)
    
    def test_update_review_success(self):
        """Test successful review update."""
        # Setup mocks
        self.mock_review_service.validate_review.return_value = None  # No validation errors
        updated_review = ProductReview(id=1, product=self.product, user=self.user, rating=4, comment='Updated comment')
        self.mock_review_service.update_review.return_value = updated_review
        
        # Request data
        update_data = {
            'rating': 4,
            'comment': 'Updated comment'
        }
        
        # Create request
        request = self.factory.put('/reviews/1/', update_data, format='json')
        
        # Mock request attributes for the test
        request.data = update_data
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='1')
        
        # Assert services were called with correct parameters
        self.mock_review_service.validate_review.assert_called_once_with(update_data)
        self.mock_review_service.update_review.assert_called_once_with('1', update_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['comment'], 'Updated comment')
    
    def test_update_review_not_found(self):
        """Test update of non-existent review."""
        # Setup mocks
        self.mock_review_service.validate_review.return_value = None  # No validation errors
        self.mock_review_service.update_review.side_effect = ValueError("Review with id 999 not found")
        
        # Request data
        update_data = {
            'rating': 4,
            'comment': 'Updated comment'
        }
        
        # Create request
        request = self.factory.put('/reviews/999/', update_data, format='json')
        
        # Mock request attributes for the test
        request.data = update_data
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='999')
        
        # Assert services were called
        self.mock_review_service.validate_review.assert_called_once_with(update_data)
        self.mock_review_service.update_review.assert_called_once_with('999', update_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Review with id 999 not found', response.data['error'])
    
    def test_update_review_validation_error(self):
        """Test review update with validation errors."""
        # Setup mock to raise ValidationError
        self.mock_review_service.validate_review.side_effect = ValidationError("Rating cannot be negative")
        
        # Request data (invalid data)
        update_data = {
            'rating': -1,  # Negative rating should fail validation
            'comment': 'Updated comment'
        }
        
        # Create request
        request = self.factory.put('/reviews/1/', update_data, format='json')
        
        # Mock request attributes for the test
        request.data = update_data
        
        # Call ViewSet method directly
        response = self.viewset.update(request, pk='1')
        
        # Assert validation service was called
        self.mock_review_service.validate_review.assert_called_once_with(update_data)
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Rating cannot be negative', response.data['error'])
    
    # DELETE Tests (DELETE /reviews/{id}/)
    
    def test_delete_review_success(self):
        """Test successful review deletion."""
        # Setup mock
        self.mock_review_service.delete_review.return_value = True
        
        # Create request
        request = self.factory.delete('/reviews/1/')
        
        # Mock request attributes for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='1')
        
        # Assert service was called with correct ID
        self.mock_review_service.delete_review.assert_called_once_with('1')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_review_not_found(self):
        """Test deletion of non-existent review."""
        # Setup mock to raise ValueError
        self.mock_review_service.delete_review.side_effect = ValueError("Review with id 999 not found")
        
        # Create request
        request = self.factory.delete('/reviews/999/')
        
        # Mock request attributes for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='999')
        
        # Assert service was called
        self.mock_review_service.delete_review.assert_called_once_with('999')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('Review with id 999 not found', response.data['error'])
    
    def test_delete_review_failure(self):
        """Test review deletion when service returns False."""
        # Setup mock to return False (deletion failed)
        self.mock_review_service.delete_review.return_value = False
        
        # Create request
        request = self.factory.delete('/reviews/1/')
        
        # Mock request attributes for the test
        request.data = {}
        
        # Call ViewSet method directly
        response = self.viewset.destroy(request, pk='1')
        
        # Assert service was called
        self.mock_review_service.delete_review.assert_called_once_with('1')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Failed to delete review', response.data['error'])
    
    # Dependency Injection Tests
    
    def test_default_service_creation(self):
        """Test that ViewSet creates default services when none provided."""
        # Create ViewSet without injecting services
        viewset = ProductReviewViewSet()
        
        # Verify default services were created
        self.assertIsNotNone(viewset.review_service)
        self.assertIsNotNone(viewset.product_service)
        
        # In production, these should be real service instances
        from products.services import ReviewService, ProductService
        self.assertIsInstance(viewset.review_service, ReviewService)
        self.assertIsInstance(viewset.product_service, ProductService)
    
    def test_injected_service_usage(self):
        """Test that injected services are used instead of defaults."""
        # Create ViewSet with injected services
        viewset = ProductReviewViewSet(
            review_service=self.mock_review_service,
            product_service=self.mock_product_service
        )
        
        # Verify injected services are used
        self.assertEqual(viewset.review_service, self.mock_review_service)
        self.assertEqual(viewset.product_service, self.mock_product_service)
