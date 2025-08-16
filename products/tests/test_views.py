"""
Tests for API views.
Tests API endpoints, serialization, and HTTP behavior.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from products.models import Category, Product, ProductReview
from products.repositories import (
    ProductRepository, CategoryRepository, ProductReviewRepository
)
from products.services import ProductService
from .factories import CategoryFactory, ProductFactory, ProductReviewFactory, UserFactory


class ProductViewSetTest(APITestCase):
    """Tests for ProductViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.category = CategoryFactory.create(name="Electronics")
        self.product = ProductFactory.create(
            name="Test Product",
            category=self.category,
            price=99.99,
            stock_quantity=10
        )
        
        # Set up repositories and service
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()
        self.review_repository = ProductReviewRepository()
        self.service = ProductService(
            product_repository=self.product_repository,
            category_repository=self.category_repository,
            review_repository=self.review_repository
        )
    
    def test_list_products(self):
        """Test GET /api/products/ endpoint."""
        # Create additional products
        for i in range(2):
            ProductFactory.create(category=self.category)
        
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 1 from setUp + 2 new ones
    
    def test_retrieve_product(self):
        """Test GET /api/products/{id}/ endpoint."""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)
        self.assertEqual(response.data['price'], str(self.product.price))
        self.assertEqual(response.data['category'], self.category.id)
    
    def test_retrieve_product_not_found(self):
        """Test GET /api/products/{id}/ with non-existent product."""
        url = reverse('product-detail', args=[99999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_product(self):
        """Test POST /api/products/ endpoint."""
        url = reverse('product-list')
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '199.99',
            'category': self.category.id,
            'stock_quantity': 5,
            'sku': 'NEW001'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Product')
        self.assertEqual(response.data['sku'], 'NEW001')
        
        # Verify product was created in database
        product = Product.objects.get(sku='NEW001')
        self.assertEqual(product.name, 'New Product')
    
    def test_create_product_invalid_data(self):
        """Test POST /api/products/ with invalid data."""
        url = reverse('product-list')
        data = {
            'name': '',  # Invalid: empty name
            'price': 'invalid_price',  # Invalid: not a number
            'category': self.category.id,
            'stock_quantity': -5,  # Invalid: negative stock
            'sku': 'NEW001'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('price', response.data)
        self.assertIn('stock_quantity', response.data)
    
    def test_create_product_duplicate_sku(self):
        """Test POST /api/products/ with duplicate SKU."""
        url = reverse('product-list')
        data = {
            'name': 'Duplicate Product',
            'description': 'Duplicate Description',
            'price': '199.99',
            'category': self.category.id,
            'stock_quantity': 5,
            'sku': self.product.sku  # Use existing SKU
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_product(self):
        """Test PUT /api/products/{id}/ endpoint."""
        url = reverse('product-detail', args=[self.product.id])
        data = {
            'name': 'Updated Product Name',
            'description': 'Updated Description',
            'price': '299.99',
            'category': self.category.id,
            'stock_quantity': 15,
            'sku': self.product.sku
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Product Name')
        self.assertEqual(response.data['price'], '299.99')
        
        # Verify product was updated in database
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.name, 'Updated Product Name')
        self.assertEqual(updated_product.price, Decimal('299.99'))
    
    def test_partial_update_product(self):
        """Test PATCH /api/products/{id}/ endpoint."""
        url = reverse('product-detail', args=[self.product.id])
        data = {
            'name': 'Partially Updated Name',
            'price': '399.99'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Partially Updated Name')
        self.assertEqual(response.data['price'], '399.99')
        
        # Verify only specified fields were updated
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.name, 'Partially Updated Name')
        self.assertEqual(updated_product.price, Decimal('399.99'))
        self.assertEqual(updated_product.description, self.product.description)  # Unchanged
    
    def test_delete_product(self):
        """Test DELETE /api/products/{id}/ endpoint."""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify product was deleted from database
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product.id)
    
    def test_delete_product_not_found(self):
        """Test DELETE /api/products/{id}/ with non-existent product."""
        url = reverse('product-detail', args=[99999])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryViewSetTest(APITestCase):
    """Tests for CategoryViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.category = CategoryFactory.create(name="Electronics")
    
    def test_list_categories(self):
        """Test GET /api/categories/ endpoint."""
        # Create test categories
        for i in range(2):
            CategoryFactory.create()
        
        url = reverse('category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 1 from setUp + 2 new ones
    
    def test_retrieve_category(self):
        """Test GET /api/categories/{id}/ endpoint."""
        url = reverse('category-detail', args=[self.category.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)
    
    def test_create_category(self):
        """Test POST /api/categories/ endpoint."""
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'New Category Description'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Category')
        
        # Verify category was created in database
        category = Category.objects.get(name='New Category')
        self.assertEqual(category.description, 'New Category Description')
    
    def test_update_category(self):
        """Test PUT /api/categories/{id}/ endpoint."""
        url = reverse('category-detail', args=[self.category.id])
        data = {
            'name': 'Updated Category Name',
            'description': 'Updated Description'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Category Name')
    
    def test_delete_category(self):
        """Test DELETE /api/categories/{id}/ endpoint."""
        url = reverse('category-detail', args=[self.category.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify category was deleted from database
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.category.id)


class ProductReviewViewSetTest(APITestCase):
    """Tests for ProductReviewViewSet API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.category = CategoryFactory.create(name="Electronics")
        self.product = ProductFactory.create(category=self.category)
        self.review = ProductReviewFactory.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment='Great product!'
        )
    
    def test_list_reviews(self):
        """Test GET /api/reviews/ endpoint."""
        # Create test reviews
        for i in range(2):
            ProductReviewFactory.create(product=self.product)
        
        url = reverse('review-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 1 from setUp + 2 new ones
    
    def test_retrieve_review(self):
        """Test GET /api/reviews/{id}/ endpoint."""
        url = reverse('review-detail', args=[self.review.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], self.review.rating)
        self.assertEqual(response.data['comment'], self.review.comment)
        self.assertEqual(response.data['product'], self.product.id)
        self.assertEqual(response.data['user'], self.user.id)
    
    def test_create_review(self):
        """Test POST /api/reviews/ endpoint."""
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 5,
            'comment': 'Excellent product!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Excellent product!')
        
        # Verify review was created in database
        review = ProductReview.objects.get(id=response.data['id'])
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
    
    def test_create_review_invalid_rating(self):
        """Test POST /api/reviews/ with invalid rating."""
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 6,  # Invalid: above maximum
            'comment': 'Invalid rating'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)
    
    def test_update_review(self):
        """Test PUT /api/reviews/{id}/ endpoint."""
        url = reverse('review-detail', args=[self.review.id])
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 5,
            'comment': 'Updated comment!'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Updated comment!')
    
    def test_delete_review(self):
        """Test DELETE /api/reviews/{id}/ endpoint."""
        url = reverse('review-detail', args=[self.review.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify review was deleted from database
        with self.assertRaises(ProductReview.DoesNotExist):
            ProductReview.objects.get(id=self.review.id)


class APIIntegrationTest(APITestCase):
    """Integration tests for complete API workflows."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.category = CategoryFactory.create(name="Electronics")
    
    def test_complete_product_workflow(self):
        """Test complete product workflow through API."""
        # 1. Create a category
        category_url = reverse('category-list')
        category_data = {'name': 'Test Category', 'description': 'Test Description'}
        category_response = self.client.post(category_url, category_data, format='json')
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        category_id = category_response.data['id']
        
        # 2. Create a product in that category
        product_url = reverse('product-list')
        product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '199.99',
            'category': category_id,
            'stock_quantity': 10,
            'sku': 'TEST001'
        }
        product_response = self.client.post(product_url, product_data, format='json')
        self.assertEqual(product_response.status_code, status.HTTP_201_CREATED)
        product_id = product_response.data['id']
        
        # 3. Create a review for the product
        review_url = reverse('review-list')
        review_data = {
            'product': product_id,
            'user': self.user.id,
            'rating': 5,
            'comment': 'Great product!'
        }
        review_response = self.client.post(review_url, review_data, format='json')
        self.assertEqual(review_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Retrieve the product and verify it has the review
        product_detail_url = reverse('product-detail', args=[product_id])
        product_response = self.client.get(product_detail_url)
        self.assertEqual(product_response.status_code, status.HTTP_200_OK)
        
        # 5. Update the product
        update_data = {'name': 'Updated Product Name'}
        update_response = self.client.patch(product_detail_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['name'], 'Updated Product Name')
        
        # 6. Delete the product (should cascade to review)
        delete_response = self.client.delete(product_detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify product and review were deleted
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=product_id)
        with self.assertRaises(ProductReview.DoesNotExist):
            ProductReview.objects.get(id=review_response.data['id'])
