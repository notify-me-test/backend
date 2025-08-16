"""
Tests for repository layer.
Tests data access patterns and repository implementations.
"""

from django.test import TestCase
from django.db import IntegrityError, models
from decimal import Decimal
from products.models import Category, Product, ProductReview
from products.repositories import (
    ProductRepository, ProductRepositoryInterface,
    CategoryRepository, CategoryRepositoryInterface,
    ProductReviewRepository, ProductReviewRepositoryInterface
)
from .factories import CategoryFactory, ProductFactory, ProductReviewFactory, UserFactory


class ProductRepositoryTest(TestCase):
    """Tests for ProductRepository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = ProductRepository()
        self.category = CategoryFactory.create()
        self.product = ProductFactory.create(category=self.category)
    
    def test_get_by_id(self):
        """Test getting product by ID."""
        result = self.repository.get_by_id(self.product.id)
        self.assertEqual(result, self.product)
    
    def test_get_by_id_not_found(self):
        """Test getting product by non-existent ID."""
        with self.assertRaises(ValueError):
            self.repository.get_by_id(99999)
    
    def test_get_all(self):
        """Test getting all products."""
        # Create additional products
        for i in range(3):
            ProductFactory.create(category=self.category)
        
        results = self.repository.get_all()
        self.assertEqual(results.count(), 4)  # 1 from setUp + 3 new ones
    

    
    def test_filter_by_category(self):
        """Test filtering products by category."""
        # Create products in different categories
        category2 = CategoryFactory.create(name="Books")
        ProductFactory.create(category=category2)
        
        # Use the actual repository method
        results = self.repository.get_by_category(self.category.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().category, self.category)
    
    def test_search_by_name(self):
        """Test searching products by name."""
        # Create products with specific names
        ProductFactory.create(name="iPhone 13", category=self.category)
        ProductFactory.create(name="iPhone 14", category=self.category)
        ProductFactory.create(name="Samsung Galaxy", category=self.category)
        
        results = self.repository.search_by_name("iPhone")
        self.assertEqual(results.count(), 2)
        self.assertTrue(all("iPhone" in p.name for p in results))
    
    def test_search_by_description(self):
        """Test searching products by description."""
        # Create products with specific descriptions
        ProductFactory.create(description="High quality smartphone", category=self.category)
        ProductFactory.create(description="Budget smartphone", category=self.category)
        ProductFactory.create(description="Gaming laptop", category=self.category)
        
        results = self.repository.search_by_description("smartphone")
        self.assertEqual(results.count(), 2)
        self.assertTrue(all("smartphone" in p.description.lower() for p in results))
    
    def test_search_by_name_or_description(self):
        """Test searching products by name or description."""
        # Create products with specific names and descriptions
        ProductFactory.create(name="iPhone", description="Apple smartphone", category=self.category)
        ProductFactory.create(name="Samsung", description="Android smartphone", category=self.category)
        ProductFactory.create(name="Laptop", description="Gaming computer", category=self.category)
        
        results = self.repository.search_by_name_or_description("smartphone")
        self.assertEqual(results.count(), 2)
        self.assertTrue(all("smartphone" in p.name.lower() or "smartphone" in p.description.lower() for p in results))
    

    
    def test_update_stock(self):
        """Test updating product stock quantity."""
        new_stock = 25
        updated_product = self.repository.update_stock(self.product.id, new_stock)
        
        self.assertEqual(updated_product.stock_quantity, new_stock)
        
        # Verify in database
        refreshed_product = Product.objects.get(id=self.product.id)
        self.assertEqual(refreshed_product.stock_quantity, new_stock)
    
    def test_update_stock_not_found(self):
        """Test updating stock for non-existent product."""
        with self.assertRaises(ValueError):
            self.repository.update_stock(99999, 25)
    



class CategoryRepositoryTest(TestCase):
    """Tests for CategoryRepository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = CategoryRepository()
        self.category = CategoryFactory.create()
    
    def test_get_by_id(self):
        """Test getting category by ID."""
        result = self.repository.get_by_id(self.category.id)
        self.assertEqual(result, self.category)
    
    def test_get_all(self):
        """Test getting all categories."""
        # Create additional categories
        for i in range(3):
            CategoryFactory.create()
        
        results = self.repository.get_all()
        self.assertEqual(results.count(), 4)  # 1 from setUp + 3 new ones
    



class ProductReviewRepositoryTest(TestCase):
    """Tests for ProductReviewRepository implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = ProductReviewRepository()
        self.user = UserFactory.create()
        self.product = ProductFactory.create()
        self.review = ProductReviewFactory.create(
            product=self.product,
            user=self.user
        )
    
    def test_get_by_id(self):
        """Test getting review by ID."""
        result = self.repository.get_by_id(self.review.id)
        self.assertEqual(result, self.review)
    
    def test_get_all(self):
        """Test getting all reviews."""
        # Create 3 additional reviews with the same product but different users
        for i in range(3):
            ProductReviewFactory.create(product=self.product)
        
        results = self.repository.get_all()
        self.assertEqual(results.count(), 4)  # 1 from setUp + 3 new ones
    

    
    def test_filter_by_product(self):
        """Test filtering reviews by product."""
        # Create reviews for different products
        product2 = ProductFactory.create()
        ProductReviewFactory.create(product=product2, user=self.user)
        
        # Use the actual repository method
        results = self.repository.get_by_product(self.product.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().product, self.product)
    
    def test_filter_by_user(self):
        """Test filtering reviews by user."""
        # Create reviews from different users
        user2 = UserFactory.create()
        ProductReviewFactory.create(product=self.product, user=user2)
        
        # Use the actual repository method
        results = self.repository.get_by_user(self.user.id)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().user, self.user)
    



class RepositoryInterfaceTest(TestCase):
    """Tests for repository interface compliance."""
    
    def test_product_repository_implements_interface(self):
        """Test that ProductRepository implements ProductRepositoryInterface."""
        repository = ProductRepository()
        self.assertIsInstance(repository, ProductRepositoryInterface)
    
    def test_category_repository_implements_interface(self):
        """Test that CategoryRepository implements CategoryRepositoryInterface."""
        repository = CategoryRepository()
        self.assertIsInstance(repository, CategoryRepositoryInterface)
    
    def test_product_review_repository_implements_interface(self):
        """Test that ProductReviewRepository implements ProductReviewRepositoryInterface."""
        repository = ProductReviewRepository()
        self.assertIsInstance(repository, ProductReviewRepositoryInterface)
