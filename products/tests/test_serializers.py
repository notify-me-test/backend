"""
Tests for serializers.
Tests data validation, serialization, and deserialization.
"""

from django.test import TestCase
from decimal import Decimal
from products.serializers import (
    CategorySerializer, ProductSerializer, ProductReviewSerializer
)
from .factories import CategoryFactory, ProductFactory, ProductReviewFactory, UserFactory


class CategorySerializerTest(TestCase):
    """Tests for CategorySerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.category = CategoryFactory.create(
            name="Electronics",
            description="Electronic products"
        )
        self.serializer = CategorySerializer(instance=self.category)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        data = self.serializer.data
        
        self.assertCountEqual(
            data.keys(),
            ['id', 'name', 'description', 'created_at', 'updated_at']
        )
    
    def test_name_field_content(self):
        """Test that name field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['name'], 'Electronics')
    
    def test_description_field_content(self):
        """Test that description field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['description'], 'Electronic products')
    
    def test_timestamp_fields(self):
        """Test that timestamp fields are present."""
        data = self.serializer.data
        
        self.assertIsNotNone(data['created_at'])
        self.assertIsNotNone(data['updated_at'])
    
    def test_create_category(self):
        """Test creating a new category through serializer."""
        data = {
            'name': 'New Category',
            'description': 'New Category Description'
        }
        
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        category = serializer.save()
        self.assertEqual(category.name, 'New Category')
        self.assertEqual(category.description, 'New Category Description')
    
    def test_create_category_invalid_data(self):
        """Test creating category with invalid data."""
        data = {
            'name': '',  # Invalid: empty name
            'description': 'Valid description'
        }
        
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_update_category(self):
        """Test updating an existing category through serializer."""
        data = {
            'name': 'Updated Category Name',
            'description': 'Updated Description'
        }
        
        serializer = CategorySerializer(self.category, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_category = serializer.save()
        self.assertEqual(updated_category.name, 'Updated Category Name')
        self.assertEqual(updated_category.description, 'Updated Description')
    
    def test_validate_name_max_length(self):
        """Test that name field respects max length constraint."""
        data = {
            'name': 'A' * 101,  # Exceeds max_length=100
            'description': 'Valid description'
        }
        
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class ProductSerializerTest(TestCase):
    """Tests for ProductSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.category = CategoryFactory.create(name="Electronics")
        self.product = ProductFactory.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
        self.serializer = ProductSerializer(instance=self.product)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        data = self.serializer.data
        
        self.assertCountEqual(
            data.keys(),
            ['id', 'name', 'description', 'price', 'category', 'stock_quantity', 'sku', 'created_at', 'updated_at']
        )
    
    def test_name_field_content(self):
        """Test that name field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['name'], 'Test Product')
    
    def test_price_field_content(self):
        """Test that price field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['price'], '99.99')
    
    def test_category_field_content(self):
        """Test that category field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['category'], self.category.id)
    
    def test_sku_field_content(self):
        """Test that SKU field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['sku'], 'TEST001')
    
    def test_create_product(self):
        """Test creating a new product through serializer."""
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '199.99',
            'category': self.category.id,
            'stock_quantity': 5,
            'sku': 'NEW001'
        }
        
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        product = serializer.save()
        self.assertEqual(product.name, 'New Product')
        self.assertEqual(product.price, Decimal('199.99'))
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.sku, 'NEW001')
    
    def test_create_product_invalid_price(self):
        """Test creating product with invalid price."""
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 'invalid_price',  # Invalid: not a number
            'category': self.category.id,
            'stock_quantity': 5,
            'sku': 'NEW001'
        }
        
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)
    
    def test_create_product_negative_stock(self):
        """Test creating product with negative stock."""
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '199.99',
            'category': self.category.id,
            'stock_quantity': -5,  # Invalid: negative stock
            'sku': 'NEW001'
        }
        
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock_quantity', serializer.errors)
    
    def test_create_product_duplicate_sku(self):
        """Test creating product with duplicate SKU."""
        data = {
            'name': 'Duplicate Product',
            'description': 'Duplicate Description',
            'price': '199.99',
            'category': self.category.id,
            'stock_quantity': 5,
            'sku': self.product.sku  # Use existing SKU
        }
        
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku', serializer.errors)
    
    def test_update_product(self):
        """Test updating an existing product through serializer."""
        data = {
            'name': 'Updated Product Name',
            'price': '299.99'
        }
        
        serializer = ProductSerializer(self.product, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_product = serializer.save()
        self.assertEqual(updated_product.name, 'Updated Product Name')
        self.assertEqual(updated_product.price, Decimal('299.99'))
        # Other fields should remain unchanged
        self.assertEqual(updated_product.description, 'Test Description')
    
    def test_validate_price_decimal_places(self):
        """Test that price field handles decimal places correctly."""
        data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.999',  # More than 2 decimal places
            'category': self.category.id,
            'stock_quantity': 10,
            'sku': 'TEST002'
        }
        
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        product = serializer.save()
        self.assertEqual(product.price, Decimal('99.999'))  # Django handles this


class ProductReviewSerializerTest(TestCase):
    """Tests for ProductReviewSerializer."""
    
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
        self.serializer = ProductReviewSerializer(instance=self.review)
    
    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        data = self.serializer.data
        
        self.assertCountEqual(
            data.keys(),
            ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        )
    
    def test_rating_field_content(self):
        """Test that rating field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['rating'], 4)
    
    def test_comment_field_content(self):
        """Test that comment field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['comment'], 'Great product!')
    
    def test_product_field_content(self):
        """Test that product field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['product'], self.product.id)
    
    def test_user_field_content(self):
        """Test that user field contains correct data."""
        data = self.serializer.data
        
        self.assertEqual(data['user'], self.user.id)
    
    def test_create_review(self):
        """Test creating a new review through serializer."""
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 5,
            'comment': 'Excellent product!'
        }
        
        serializer = ProductReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        review = serializer.save()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent product!')
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
    
    def test_create_review_invalid_rating_low(self):
        """Test creating review with rating below minimum."""
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 0,  # Invalid: below minimum
            'comment': 'Invalid rating'
        }
        
        serializer = ProductReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)
    
    def test_create_review_invalid_rating_high(self):
        """Test creating review with rating above maximum."""
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 6,  # Invalid: above maximum
            'comment': 'Invalid rating'
        }
        
        serializer = ProductReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)
    
    def test_create_review_valid_ratings(self):
        """Test creating reviews with all valid ratings."""
        for rating in [1, 2, 3, 4, 5]:
            data = {
                'product': self.product.id,
                'user': self.user.id,
                'rating': rating,
                'comment': f'Rating {rating} review'
            }
            
            serializer = ProductReviewSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Rating {rating} should be valid")
    
    def test_create_review_empty_comment(self):
        """Test creating review with empty comment (should be valid)."""
        data = {
            'product': self.product.id,
            'user': self.user.id,
            'rating': 4,
            'comment': ''  # Empty comment should be valid
        }
        
        serializer = ProductReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        review = serializer.save()
        self.assertEqual(review.comment, '')
    
    def test_update_review(self):
        """Test updating an existing review through serializer."""
        data = {
            'rating': 5,
            'comment': 'Updated comment!'
        }
        
        serializer = ProductReviewSerializer(self.review, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_review = serializer.save()
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(updated_review.comment, 'Updated comment!')
        # Other fields should remain unchanged
        self.assertEqual(updated_review.product, self.product)
        self.assertEqual(updated_review.user, self.user)


class SerializerValidationTest(TestCase):
    """Tests for serializer validation logic."""
    
    def setUp(self):
        """Set up test data."""
        self.category = CategoryFactory.create(name="Electronics")
        self.user = UserFactory.create()
        self.product = ProductFactory.create(category=self.category)
    
    def test_product_serializer_required_fields(self):
        """Test that ProductSerializer requires all necessary fields."""
        # Missing required fields
        data = {
            'name': 'Test Product',
            # Missing: description, price, category, stock_quantity, sku
        }
        
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Check that all required fields are mentioned in errors
        required_fields = ['description', 'price', 'category', 'stock_quantity', 'sku']
        for field in required_fields:
            self.assertIn(field, serializer.errors)
    
    def test_review_serializer_required_fields(self):
        """Test that ProductReviewSerializer requires all necessary fields."""
        # Missing required fields
        data = {
            'rating': 5,
            # Missing: product, user
        }
        
        serializer = ProductReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Check that all required fields are mentioned in errors
        required_fields = ['product', 'user']
        for field in required_fields:
            self.assertIn(field, serializer.errors)
    
    def test_serializer_data_integrity(self):
        """Test that serialized data maintains integrity."""
        # Create a product
        product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': '99.99',
            'category': self.category.id,
            'stock_quantity': 10,
            'sku': 'TEST001'
        }
        
        serializer = ProductSerializer(data=product_data)
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        
        # Serialize the product back
        serialized_data = ProductSerializer(product).data
        
        # Verify data integrity
        self.assertEqual(serialized_data['name'], product_data['name'])
        self.assertEqual(serialized_data['description'], product_data['description'])
        self.assertEqual(serialized_data['price'], product_data['price'])
        self.assertEqual(serialized_data['category'], product_data['category'])
        self.assertEqual(serialized_data['stock_quantity'], product_data['stock_quantity'])
        self.assertEqual(serialized_data['sku'], product_data['sku'])
