from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Product, ProductReview
import json

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description", 
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 99.99)
    
    def test_check_stock_positive(self):
        result = self.product.check_stock()
        self.assertTrue(result)

class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
    
    def test_get_products_list(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_product(self):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 199.99,
            'category': self.category.id,
            'stock_quantity': 5,
            'sku': 'NEW001'
        }
        response = self.client.post('/api/products/', data)

class CategoryTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Books")
        self.assertEqual(category.name, "Books")
