"""
Test utilities and base classes for products app tests.
Provides common test setup, fixtures, and helper methods.
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from products.models import Category, Product, ProductReview


class BaseProductTestCase(TestCase):
    """Base test case for product-related tests with common setup."""
    
    def setUp(self):
        """Set up common test data."""
        super().setUp()
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )


class BaseProductAPITestCase(APITestCase):
    """Base test case for product API tests with common setup."""
    
    def setUp(self):
        """Set up common test data for API tests."""
        super().setUp()
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )


class BaseRepositoryTestCase(TestCase):
    """Base test case for repository tests."""
    
    def setUp(self):
        """Set up common test data for repository tests."""
        super().setUp()
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )


class BaseServiceTestCase(TestCase):
    """Base test case for service layer tests."""
    
    def setUp(self):
        """Set up common test data for service tests."""
        super().setUp()
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
