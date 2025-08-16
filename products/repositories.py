from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from .models import Product, Category, ProductReview


class ProductRepositoryInterface(ABC):
    """
    Abstract base class for product data access operations.
    Defines the contract for product repository implementations.
    """
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        """Get all products."""
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Product:
        """Get product by ID."""
        pass
    
    @abstractmethod
    def get_by_category(self, category_id: int) -> QuerySet:
        """Get products by category ID."""
        pass
    
    @abstractmethod
    def get_by_price_range(self, min_price: float, max_price: float) -> QuerySet:
        """Get products within price range."""
        pass
    
    @abstractmethod
    def get_low_stock(self, threshold: int) -> QuerySet:
        """Get products with stock below or equal to threshold."""
        pass
    
    @abstractmethod
    def search_by_name(self, query: str) -> QuerySet:
        """Search products by name."""
        pass
    
    @abstractmethod
    def search_by_description(self, query: str) -> QuerySet:
        """Search products by description."""
        pass
    
    @abstractmethod
    def search_by_name_or_description(self, query: str) -> QuerySet:
        """Search products by name or description."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> Product:
        """Create a new product."""
        pass
    
    @abstractmethod
    def update(self, product_id: int, **kwargs) -> Product:
        """Update an existing product."""
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Delete a product."""
        pass
    
    @abstractmethod
    def update_stock(self, product_id: int, new_stock: int) -> Product:
        """Update product stock quantity."""
        pass


class CategoryRepositoryInterface(ABC):
    """
    Abstract base class for category data access operations.
    Defines the contract for category repository implementations.
    """
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        """Get all categories."""
        pass
    
    @abstractmethod
    def get_by_id(self, category_id: int) -> Category:
        """Get category by ID."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> Category:
        """Create a new category."""
        pass
    
    @abstractmethod
    def update(self, category_id: int, **kwargs) -> Category:
        """Update an existing category."""
        pass
    
    @abstractmethod
    def delete(self, category_id: int) -> bool:
        """Delete a category."""
        pass


class ProductReviewRepositoryInterface(ABC):
    """
    Abstract base class for product review data access operations.
    Defines the contract for product review repository implementations.
    """
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        """Get all product reviews."""
        pass
    
    @abstractmethod
    def get_by_id(self, review_id: int) -> ProductReview:
        """Get review by ID."""
        pass
    
    @abstractmethod
    def get_by_product(self, product_id: int) -> QuerySet:
        """Get reviews by product ID."""
        pass
    
    @abstractmethod
    def get_by_user(self, user_id: int) -> QuerySet:
        """Get reviews by user ID."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> ProductReview:
        """Create a new review."""
        pass
    
    @abstractmethod
    def update(self, review_id: int, **kwargs) -> ProductReview:
        """Update an existing review."""
        pass
    
    @abstractmethod
    def delete(self, review_id: int) -> bool:
        """Delete a review."""
        pass


class ProductRepository(ProductRepositoryInterface):
    """
    Concrete implementation of ProductRepositoryInterface using Django ORM.
    """
    
    def get_all(self) -> QuerySet:
        """Get all products."""
        return Product.objects.all()
    
    def create(self, **kwargs) -> Product:
        """Create a new product."""
        try:
            return Product.objects.create(**kwargs)
        except Exception as e:
            raise ValueError(f"Error creating product: {str(e)}")
    
    def update(self, product_id: int, **kwargs) -> Product:
        """Update an existing product."""
        try:
            product = Product.objects.get(id=product_id)
            for key, value in kwargs.items():
                setattr(product, key, value)
            product.save()
            return product
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} not found")
        except Exception as e:
            raise ValueError(f"Error updating product {product_id}: {str(e)}")
    
    def delete(self, product_id: int) -> bool:
        """Delete a product."""
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return True
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} not found")
        except Exception as e:
            raise ValueError(f"Error deleting product {product_id}: {str(e)}")
    
    def get_by_id(self, product_id: int) -> Product:
        """Get product by ID."""
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} not found")
        except Exception as e:
            raise ValueError(f"Error retrieving product {product_id}: {str(e)}")
    
    def get_by_category(self, category_id: int) -> QuerySet:
        """Get products by category ID."""
        return Product.objects.filter(category_id=category_id)
    
    def get_by_price_range(self, min_price: float, max_price: float) -> QuerySet:
        """Get products within price range."""
        return Product.objects.filter(price__gte=min_price, price__lte=max_price)
    
    def get_low_stock(self, threshold: int) -> QuerySet:
        """Get products with stock below or equal to threshold."""
        return Product.objects.filter(stock_quantity__lte=threshold)
    
    def search_by_name(self, query: str) -> QuerySet:
        """Search products by name."""
        return Product.objects.filter(name__icontains=query)
    
    def search_by_description(self, query: str) -> QuerySet:
        """Search products by description."""
        return Product.objects.filter(description__icontains=query)
    
    def search_by_name_or_description(self, query: str) -> QuerySet:
        """Search products by name or description."""
        from django.db.models import Q
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    def update_stock(self, product_id: int, new_stock: int) -> Product:
        """Update product stock quantity."""
        try:
            product = Product.objects.get(id=product_id)
            product.stock_quantity = new_stock
            product.save()
            return product
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} not found")
        except Exception as e:
            raise ValueError(f"Error updating product {product_id}: {str(e)}")


class CategoryRepository(CategoryRepositoryInterface):
    """
    Concrete implementation of CategoryRepositoryInterface using Django ORM.
    """
    
    def get_all(self) -> QuerySet:
        """Get all categories."""
        return Category.objects.all()
    
    def get_by_id(self, category_id: int) -> Category:
        """Get category by ID."""
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise ValueError(f"Category with id {category_id} not found")
        except Exception as e:
            raise ValueError(f"Error retrieving category {category_id}: {str(e)}")
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None
        except Exception as e:
            raise ValueError(f"Error retrieving category by name {name}: {str(e)}")
    
    def create(self, **kwargs) -> Category:
        """Create a new category."""
        try:
            return Category.objects.create(**kwargs)
        except Exception as e:
            raise ValueError(f"Error creating category: {str(e)}")
    
    def update(self, category_id: int, **kwargs) -> Category:
        """Update an existing category."""
        try:
            category = Category.objects.get(id=category_id)
            for key, value in kwargs.items():
                setattr(category, key, value)
            category.save()
            return category
        except Category.DoesNotExist:
            raise ValueError(f"Category with id {category_id} not found")
        except Exception as e:
            raise ValueError(f"Error updating category {category_id}: {str(e)}")
    
    def delete(self, category_id: int) -> bool:
        """Delete a category."""
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return True
        except Category.DoesNotExist:
            raise ValueError(f"Category with id {category_id} not found")
        except Exception as e:
            raise ValueError(f"Error deleting category {category_id}: {str(e)}")


class ProductReviewRepository(ProductReviewRepositoryInterface):
    """
    Concrete implementation of ProductReviewRepositoryInterface using Django ORM.
    """
    
    def get_all(self) -> QuerySet:
        """Get all product reviews."""
        return ProductReview.objects.all()
    
    def get_by_id(self, review_id: int) -> ProductReview:
        """Get review by ID."""
        try:
            return ProductReview.objects.get(id=review_id)
        except ProductReview.DoesNotExist:
            raise ValueError(f"Review with id {review_id} not found")
        except Exception as e:
            raise ValueError(f"Error retrieving review {review_id}: {str(e)}")
    
    def get_by_product(self, product_id: int) -> QuerySet:
        """Get reviews by product ID."""
        return ProductReview.objects.filter(product_id=product_id)
    
    def get_by_user(self, user_id: int) -> QuerySet:
        """Get reviews by user ID."""
        return ProductReview.objects.filter(user_id=user_id)
    
    def create(self, **kwargs) -> ProductReview:
        """Create a new review."""
        try:
            return ProductReview.objects.create(**kwargs)
        except Exception as e:
            raise ValueError(f"Error creating review: {str(e)}")
    
    def update(self, review_id: int, **kwargs) -> ProductReview:
        """Update an existing review."""
        try:
            review = ProductReview.objects.get(id=review_id)
            for key, value in kwargs.items():
                setattr(review, key, value)
            review.save()
            return review
        except ProductReview.DoesNotExist:
            raise ValueError(f"Review with id {review_id} not found")
        except Exception as e:
            raise ValueError(f"Error updating review {review_id}: {str(e)}")
    
    def delete(self, review_id: int) -> bool:
        """Delete a review."""
        try:
            review = ProductReview.objects.get(id=review_id)
            review.delete()
            return True
        except ProductReview.DoesNotExist:
            raise ValueError(f"Review with id {review_id} not found")
        except Exception as e:
            raise ValueError(f"Error deleting review {review_id}: {str(e)}")
