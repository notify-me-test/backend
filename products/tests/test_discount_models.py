from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category, ProductDiscount


class ProductDiscountModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description",
            price=100.00,
            category=self.category,
            stock_quantity=10,
            sku="TEST123",
            is_active=True
        )
    
    def test_create_valid_discount(self):
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.50,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        self.assertEqual(discount.product, self.product)
        self.assertEqual(discount.discount_percentage, 15.50)
        self.assertEqual(discount.start_date, start_date)
        self.assertEqual(discount.end_date, end_date)
        self.assertTrue(discount.is_active)
        self.assertIsNotNone(discount.created_at)
        self.assertIsNotNone(discount.updated_at)
    
    def test_discount_percentage_validation(self):
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        # Test negative percentage
        with self.assertRaises(ValidationError):
            discount = ProductDiscount(
                product=self.product,
                discount_percentage=-5.00,
                start_date=start_date,
                end_date=end_date
            )
            discount.full_clean()
        
        # Test percentage over 100
        with self.assertRaises(ValidationError):
            discount = ProductDiscount(
                product=self.product,
                discount_percentage=105.00,
                start_date=start_date,
                end_date=end_date
            )
            discount.full_clean()
    
    def test_date_validation(self):
        start_date = timezone.now()
        end_date = start_date - timedelta(days=1)  # End date before start date
        
        with self.assertRaises(ValidationError):
            discount = ProductDiscount(
                product=self.product,
                discount_percentage=15.50,
                start_date=start_date,
                end_date=end_date
            )
            discount.full_clean()
    
    def test_product_relationship(self):
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=start_date,
            end_date=end_date
        )
        
        # Test that discount is accessible from product
        self.assertIn(discount, self.product.discounts.all())
    
    def test_discount_string_representation(self):
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=25.00,
            start_date=start_date,
            end_date=end_date
        )
        
        expected_str = f"{self.product.name} - 25.0% discount"
        self.assertEqual(str(discount), expected_str)
    
    def test_multiple_discounts_per_product(self):
        now = timezone.now()
        
        # Create two non-overlapping discounts for same product
        discount1 = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=10.00,
            start_date=now,
            end_date=now + timedelta(days=5)
        )
        
        discount2 = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=now + timedelta(days=10),
            end_date=now + timedelta(days=15)
        )
        
        self.assertEqual(self.product.discounts.count(), 2)
        self.assertIn(discount1, self.product.discounts.all())
        self.assertIn(discount2, self.product.discounts.all())
    
    def test_discount_default_values(self):
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.50,
            start_date=start_date,
            end_date=end_date
        )
        
        # Test default value for is_active
        self.assertTrue(discount.is_active)
    
    def test_discount_cascade_delete(self):
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.50,
            start_date=start_date,
            end_date=end_date
        )
        
        discount_id = discount.id
        
        # Delete the product
        self.product.delete()
        
        # Check that discount was also deleted
        with self.assertRaises(ProductDiscount.DoesNotExist):
            ProductDiscount.objects.get(id=discount_id)