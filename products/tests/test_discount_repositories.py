from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category, ProductDiscount
from products.repositories import ProductDiscountRepository


class ProductDiscountRepositoryTest(TestCase):
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
        self.repository = ProductDiscountRepository()
        self.now = timezone.now()
    
    def test_get_all_discounts(self):
        discount1 = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.00,
            start_date=self.now,
            end_date=self.now + timedelta(days=7)
        )
        discount2 = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=25.00,
            start_date=self.now + timedelta(days=10),
            end_date=self.now + timedelta(days=17)
        )
        
        discounts = self.repository.get_all()
        self.assertEqual(discounts.count(), 2)
        self.assertIn(discount1, discounts)
        self.assertIn(discount2, discounts)
    
    def test_get_discount_by_id(self):
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=self.now,
            end_date=self.now + timedelta(days=5)
        )
        
        retrieved_discount = self.repository.get_by_id(discount.id)
        self.assertEqual(retrieved_discount, discount)
    
    def test_get_discount_by_id_not_found(self):
        with self.assertRaises(ValueError) as context:
            self.repository.get_by_id(999)
        self.assertIn("not found", str(context.exception))
    
    def test_create_discount(self):
        discount_data = {
            'product': self.product,
            'discount_percentage': 30.00,
            'start_date': self.now,
            'end_date': self.now + timedelta(days=14),
            'is_active': True
        }
        
        discount = self.repository.create(**discount_data)
        self.assertEqual(discount.product, self.product)
        self.assertEqual(discount.discount_percentage, 30.00)
        self.assertTrue(discount.is_active)
    
    def test_update_discount(self):
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.00,
            start_date=self.now,
            end_date=self.now + timedelta(days=7)
        )
        
        updated_discount = self.repository.update(discount.id, discount_percentage=25.00)
        self.assertEqual(updated_discount.discount_percentage, 25.00)
        self.assertEqual(updated_discount.id, discount.id)
    
    def test_update_discount_not_found(self):
        with self.assertRaises(ValueError):
            self.repository.update(999, discount_percentage=25.00)
    
    def test_delete_discount(self):
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.00,
            start_date=self.now,
            end_date=self.now + timedelta(days=7)
        )
        discount_id = discount.id
        
        result = self.repository.delete(discount_id)
        self.assertTrue(result)
        
        with self.assertRaises(ProductDiscount.DoesNotExist):
            ProductDiscount.objects.get(id=discount_id)
    
    def test_delete_discount_not_found(self):
        with self.assertRaises(ValueError):
            self.repository.delete(999)
    
    def test_get_active_discount_for_product_current_active(self):
        # Create an active discount for the current time
        active_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=self.now - timedelta(hours=1),
            end_date=self.now + timedelta(days=5),
            is_active=True
        )
        
        result = self.repository.get_active_discount_for_product(self.product.id, self.now)
        self.assertEqual(result, active_discount)
    
    def test_get_active_discount_for_product_not_started(self):
        # Create a discount that hasn't started yet
        future_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=self.now + timedelta(days=1),
            end_date=self.now + timedelta(days=5),
            is_active=True
        )
        
        result = self.repository.get_active_discount_for_product(self.product.id, self.now)
        self.assertIsNone(result)
    
    def test_get_active_discount_for_product_expired(self):
        # Create an expired discount
        expired_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=self.now - timedelta(days=10),
            end_date=self.now - timedelta(days=5),
            is_active=True
        )
        
        result = self.repository.get_active_discount_for_product(self.product.id, self.now)
        self.assertIsNone(result)
    
    def test_get_active_discount_for_product_inactive(self):
        # Create an inactive discount
        inactive_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=self.now - timedelta(hours=1),
            end_date=self.now + timedelta(days=5),
            is_active=False
        )
        
        result = self.repository.get_active_discount_for_product(self.product.id, self.now)
        self.assertIsNone(result)
    
    def test_get_active_discount_for_product_multiple_discounts_returns_latest(self):
        # Create multiple active discounts for the same product
        older_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=15.00,
            start_date=self.now - timedelta(days=2),
            end_date=self.now + timedelta(days=5),
            is_active=True
        )
        newer_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=25.00,
            start_date=self.now - timedelta(hours=1),
            end_date=self.now + timedelta(days=3),
            is_active=True
        )
        
        result = self.repository.get_active_discount_for_product(self.product.id, self.now)
        self.assertEqual(result, newer_discount)
    
    def test_get_all_active_discounts(self):
        # Create products with different discount states
        product2 = Product.objects.create(
            name="Product 2",
            description="Product 2 description",
            price=200.00,
            category=self.category,
            stock_quantity=5,
            sku="TEST456"
        )
        
        # Active discount for product 1
        active_discount1 = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=20.00,
            start_date=self.now - timedelta(hours=1),
            end_date=self.now + timedelta(days=5),
            is_active=True
        )
        
        # Active discount for product 2
        active_discount2 = ProductDiscount.objects.create(
            product=product2,
            discount_percentage=30.00,
            start_date=self.now - timedelta(hours=2),
            end_date=self.now + timedelta(days=3),
            is_active=True
        )
        
        # Expired discount
        expired_discount = ProductDiscount.objects.create(
            product=self.product,
            discount_percentage=40.00,
            start_date=self.now - timedelta(days=10),
            end_date=self.now - timedelta(days=5),
            is_active=True
        )
        
        # Inactive discount
        inactive_discount = ProductDiscount.objects.create(
            product=product2,
            discount_percentage=50.00,
            start_date=self.now - timedelta(hours=1),
            end_date=self.now + timedelta(days=5),
            is_active=False
        )
        
        active_discounts = self.repository.get_all_active_discounts(self.now)
        self.assertEqual(active_discounts.count(), 2)
        self.assertIn(active_discount1, active_discounts)
        self.assertIn(active_discount2, active_discounts)
        self.assertNotIn(expired_discount, active_discounts)
        self.assertNotIn(inactive_discount, active_discounts)