"""
Test data factories for products app tests.
Provides consistent and maintainable test data creation using Factory Boy.
"""

import factory
from django.contrib.auth.models import User
from products.models import Category, Product, ProductReview


class CategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating Category test instances."""
    
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category {n+1}')
    description = factory.Sequence(lambda n: f'Description for category {n+1}')


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for creating Product test instances."""
    
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f'Product {n+1}')
    description = factory.Sequence(lambda n: f'Description for product {n+1}')
    price = factory.Sequence(lambda n: 99.99 + (n * 10))
    category = factory.SubFactory(CategoryFactory)
    stock_quantity = factory.Sequence(lambda n: 10 + n)
    sku = factory.Sequence(lambda n: f'TEST{(n+1):03d}')
    is_active = True


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User test instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'testuser{n+1}')
    email = factory.Sequence(lambda n: f'test{n+1}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_staff = False
    is_superuser = False


class ProductReviewFactory(factory.django.DjangoModelFactory):
    """Factory for creating ProductReview test instances."""
    
    class Meta:
        model = ProductReview
    
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Sequence(lambda n: 1 + (n % 5))
    comment = factory.Sequence(lambda n: f'Review comment {n+1}')


# Legacy methods for backward compatibility (if needed)
def create_batch_factory(factory_class, count=3, **kwargs):
    """Create multiple instances using Factory Boy's create_batch."""
    return factory_class.create_batch(count, **kwargs)
