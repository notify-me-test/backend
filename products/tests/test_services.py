"""
Tests for service layer.
Tests business logic and service methods.
"""

from django.test import TestCase
from decimal import Decimal
from products.services import ProductService
from products.repositories import (
    ProductRepository, CategoryRepository, ProductReviewRepository
)
from products.models import Product
from .factories import CategoryFactory, ProductFactory, ProductReviewFactory, UserFactory


class ProductServiceTest(TestCase):
    """Tests for ProductService business logic."""
    
    def setUp(self):
        """Set up test data and service."""
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.review_repository = ProductReviewRepository()
        
        self.service = ProductService(
            product_repository=self.product_repository,
            category_repository=self.category_repository,
            review_repository=self.review_repository
        )
        
        # Create test data
        self.category = CategoryFactory.create(name="Electronics")
        self.product = ProductFactory.create(
            name="Test Product",
            category=self.category,
            stock_quantity=10,
            price=99.99
        )
        self.user = UserFactory.create()
    
    def test_update_product_stock_success(self):
        """Test successful stock update."""
        new_stock = 15
        
        result = self.service.update_product_stock(self.product.id, new_stock)
        
        self.assertIn('message', result)
        self.assertEqual(result['new_stock'], new_stock)
        
        # Verify stock was updated
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.stock_quantity, new_stock)
    
    def test_update_product_stock_negative(self):
        """Test stock update with negative value."""
        result = self.service.update_product_stock(self.product.id, -5)
        
        self.assertIn('error', result)
        self.assertIn('cannot be negative', result['error'])
        
        # Verify stock was not changed
        unchanged_product = Product.objects.get(id=self.product.id)
        self.assertEqual(unchanged_product.stock_quantity, 10)
    
    def test_update_product_stock_product_not_found(self):
        """Test stock update for non-existent product."""
        result = self.service.update_product_stock(99999, 20)
        
        self.assertIn('error', result)
    

    
    def test_get_low_stock_products_custom_threshold(self):
        """Test getting low stock products with custom threshold."""
        # Create products with different stock levels
        ProductFactory.create(stock_quantity=8, category=self.category)   # Below threshold
        ProductFactory.create(stock_quantity=12, category=self.category)  # Above threshold
        
        results = self.service.get_low_stock_products(threshold=10)
        
        self.assertEqual(results.count(), 1)  # Only 8 stock
        self.assertEqual(results.first().stock_quantity, 8)
    
    def test_get_low_stock_products_no_low_stock(self):
        """Test getting low stock products when none exist."""
        # Create products with high stock
        ProductFactory.create(stock_quantity=20, category=self.category)
        ProductFactory.create(stock_quantity=25, category=self.category)
        
        results = self.service.get_low_stock_products(threshold=10)
        
        self.assertEqual(results.count(), 0)
    
    def test_get_products_with_filters_and_enrichment(self):
        """Test getting products with filters and enrichment."""
        # Create additional products
        ProductFactory.create(name="iPhone 13", price=999.99, category=self.category)
        ProductFactory.create(name="Samsung Galaxy", price=799.99, category=self.category)
        
        # Test filtering by category
        results = self.service.get_products_with_filters_and_enrichment({
            'category': self.category.id
        })
        
        self.assertEqual(results.count(), 3)  # All products in category
        self.assertTrue(all(p.category == self.category for p in results))
    
    def test_get_products_with_filters_and_enrichment_price_range(self):
        """Test filtering products by price range."""
        # Create products with different prices
        ProductFactory.create(name="Budget Product", price=50.00, category=self.category)
        ProductFactory.create(name="Premium Product", price=150.00, category=self.category)
        
        results = self.service.get_products_with_filters_and_enrichment({
            'min_price': 75.00,
            'max_price': 125.00
        })
        
        # Should include products with prices between 75 and 125
        self.assertTrue(all(75.00 <= p.price <= 125.00 for p in results))
    

    
    def test_search_products(self):
        """Test product search functionality."""
        # Create products with searchable names
        ProductFactory.create(name="iPhone 13 Pro", category=self.category)
        ProductFactory.create(name="iPhone 14 Pro", category=self.category)
        ProductFactory.create(name="Samsung Galaxy S23", category=self.category)
        
        # Search for iPhone
        results = self.service.search_products("iPhone")
        
        self.assertEqual(results.count(), 2)
        self.assertTrue(all("iPhone" in p.name for p in results))
    
    def test_search_products_case_insensitive(self):
        """Test that search is case insensitive."""
        ProductFactory.create(name="IPHONE 13", category=self.category)
        ProductFactory.create(name="iphone 14", category=self.category)
        
        results = self.service.search_products("iphone")
        
        self.assertEqual(results.count(), 2)
    
    def test_search_products_no_results(self):
        """Test search with no matching results."""
        results = self.service.search_products("NonExistentProduct")
        
        self.assertEqual(results.count(), 0)
    
    def test_search_products_empty_query(self):
        """Test search with empty query."""
        results = self.service.search_products("")
        
        # Should return all products
        self.assertEqual(results.count(), 1)  # Only the product from setUp
    
    def test_get_reviews_by_product(self):
        """Test getting reviews for a specific product."""
        # Create reviews for the product
        ProductReviewFactory.create(product=self.product, user=self.user, rating=4)
        ProductReviewFactory.create(product=self.product, user=self.user, rating=5)
        
        # Create review for different product
        other_product = ProductFactory.create(category=self.category)
        ProductReviewFactory.create(product=other_product, user=self.user, rating=3)
        
        results = self.service.get_reviews_by_product(self.product.id)
        
        self.assertEqual(results.count(), 2)
        self.assertTrue(all(r.product == self.product for r in results))
    
    def test_get_reviews_by_product_no_reviews(self):
        """Test getting reviews for product with no reviews."""
        results = self.service.get_reviews_by_product(self.product.id)
        
        self.assertEqual(results.count(), 0)
    
    def test_get_reviews_by_product_product_not_found(self):
        """Test getting reviews for non-existent product."""
        results = self.service.get_reviews_by_product(99999)
        
        self.assertEqual(results.count(), 0)
    



class ProductServiceIntegrationTest(TestCase):
    """Integration tests for ProductService with real repositories."""
    
    def setUp(self):
        """Set up test data and service."""
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.review_repository = ProductReviewRepository()
        
        self.service = ProductService(
            product_repository=self.product_repository,
            category_repository=self.category_repository,
            review_repository=self.review_repository
        )
        
        # Create test data
        self.category = CategoryFactory.create(name="Electronics")
        self.product = ProductFactory.create(category=self.category)
        self.user = UserFactory.create()
    

