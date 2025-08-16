"""
Tests for product models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from products.models import Category, Product, ProductReview, ProductImage


class CategoryModelTest(TestCase):
    """Tests for Category model data structure and basic functionality."""
    
    def test_category_creation(self):
        """Test that category can be created with basic fields."""
        category = Category.objects.create(
            name="Electronics",
            description="Electronic products and gadgets"
        )
        
        # Verify field assignments
        self.assertEqual(category.name, "Electronics")
        self.assertEqual(category.description, "Electronic products and gadgets")
        self.assertIsNotNone(category.id)
    
    def test_category_string_representation(self):
        """Test that __str__ method returns the category name."""
        category = Category.objects.create(name="Books")
        
        self.assertEqual(str(category), "Books")
    
    def test_category_description_optional(self):
        """Test that description field is optional."""
        category = Category.objects.create(name="Clothing")
        
        # Description should be empty string by default
        self.assertEqual(category.description, "")
        
        # Should be able to set description later
        category.description = "Fashion and apparel"
        category.save()
        
        # Refresh from database
        category.refresh_from_db()
        self.assertEqual(category.description, "Fashion and apparel")
    
    def test_category_with_parent(self):
        """Test parent-child category relationships."""
        # Create parent category
        parent = Category.objects.create(name="Electronics")
        
        # Create child category
        child = Category.objects.create(
            name="Smartphones",
            parent=parent
        )
        
        # Verify relationships
        self.assertEqual(child.parent, parent)
        self.assertEqual(child.parent.name, "Electronics")
        
        # Test reverse relationship
        self.assertIn(child, parent.category_set.all())
    
    def test_category_without_parent(self):
        """Test that category can exist without parent."""
        category = Category.objects.create(name="Electronics")
        
        # Parent should be None
        self.assertIsNone(category.parent)


class ProductModelTest(TestCase):
    """Tests for Product model data structure and basic functionality."""
    
    def setUp(self):
        """Create basic test data for each test."""
        self.category = Category.objects.create(name="Electronics")
    
    def test_product_creation(self):
        """Test that product can be created with all required fields."""
        product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
        
        # Verify field assignments
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "Test Description")
        self.assertEqual(product.price, Decimal('99.99'))
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.stock_quantity, 10)
        self.assertEqual(product.sku, "TEST001")
        self.assertTrue(product.is_active)
        self.assertIsNotNone(product.id)
    
    def test_product_string_representation(self):
        """Test that __str__ method returns the product name."""
        product = Product.objects.create(
            name="iPhone 13",
            description="Smartphone",
            price=Decimal('999.99'),
            category=self.category,
            stock_quantity=5,
            sku="IPHONE13"
        )
        
        self.assertEqual(str(product), "iPhone 13")
    
    def test_product_field_types(self):
        """Test that fields have correct types."""
        product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST002"
        )
        
        # Test field types
        self.assertIsInstance(product.price, Decimal)
        self.assertIsInstance(product.stock_quantity, int)
        self.assertIsInstance(product.is_active, bool)
        self.assertIsInstance(product.name, str)
    
    def test_product_relationships(self):
        """Test product-category relationship."""
        product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST003"
        )
        
        # Test forward relationship
        self.assertEqual(product.category, self.category)
        
        # Test reverse relationship
        self.assertIn(product, self.category.product_set.all())
    
    def test_product_timestamps(self):
        """Test that timestamps are automatically set."""
        product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST004"
        )
        
        # Test that timestamps are set
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
    
    def test_product_default_values(self):
        """Test that default values are set correctly."""
        product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST005"
        )
        
        # Test default values
        self.assertTrue(product.is_active)


class ProductImageModelTest(TestCase):
    """Tests for ProductImage model data structure and basic functionality."""
    
    def setUp(self):
        """Create basic test data for each test."""
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
    
    def test_product_image_creation(self):
        """Test that product image can be created with basic fields."""
        # Note: We can't actually test ImageField without a real image file
        # So we'll test the other fields
        product_image = ProductImage.objects.create(
            product=self.product,
            alt_text="Test image",
            is_primary=False
        )
        
        # Verify field assignments
        self.assertEqual(product_image.product, self.product)
        self.assertEqual(product_image.alt_text, "Test image")
        self.assertFalse(product_image.is_primary)
        self.assertIsNotNone(product_image.id)
    
    def test_product_image_string_representation(self):
        """Test that __str__ method returns formatted string."""
        product_image = ProductImage.objects.create(
            product=self.product,
            alt_text="Test image",
            is_primary=False
        )
        
        expected_string = f"{self.product.name} - Image"
        self.assertEqual(str(product_image), expected_string)
    
    def test_product_image_relationships(self):
        """Test product image-product relationship."""
        product_image = ProductImage.objects.create(
            product=self.product,
            alt_text="Test image",
            is_primary=False
        )
        
        # Test forward relationship
        self.assertEqual(product_image.product, self.product)
        
        # Test reverse relationship
        self.assertIn(product_image, self.product.productimage_set.all())
    
    def test_product_image_default_values(self):
        """Test that default values are set correctly."""
        product_image = ProductImage.objects.create(
            product=self.product,
            alt_text="Test image"
        )
        
        # Test default values
        self.assertFalse(product_image.is_primary)


class ProductReviewModelTest(TestCase):
    """Tests for ProductReview model data structure and basic functionality."""
    
    def setUp(self):
        """Create basic test data for each test."""
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=10,
            sku="TEST001"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_review_creation(self):
        """Test that review can be created with all required fields."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product!"
        )
        
        # Verify field assignments
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great product!")
        self.assertIsNotNone(review.id)
    
    def test_review_string_representation(self):
        """Test that __str__ method returns formatted string."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment="Good product"
        )
        
        expected_string = f"{self.product.name} - 4 stars"
        self.assertEqual(str(review), expected_string)
    
    def test_review_relationships(self):
        """Test review-product and review-user relationships."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product!"
        )
        
        # Test product relationship
        self.assertEqual(review.product, self.product)
        self.assertIn(review, self.product.productreview_set.all())
        
        # Test user relationship
        self.assertEqual(review.user, self.user)
    
    def test_review_timestamps(self):
        """Test that created_at timestamp is automatically set."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product!"
        )
        
        # Test that timestamp is set
        self.assertIsNotNone(review.created_at)
    
    def test_review_field_types(self):
        """Test that fields have correct types."""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product!"
        )
        
        # Test field types
        self.assertIsInstance(review.rating, int)
        self.assertIsInstance(review.comment, str)
        self.assertIsInstance(review.product, Product)
        self.assertIsInstance(review.user, User)
