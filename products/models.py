from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField()
    sku = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def check_stock(self):
        """Check if product has stock available."""
        return self.stock_quantity > 0
    
    def clean(self):
        """Validate business rules."""
        from django.core.exceptions import ValidationError
        
        if self.price < 0:
            raise ValidationError("Price cannot be negative")
        
        if self.stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation."""
        self.clean()
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product.name} - Image"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"
    
    def clean(self):
        """Validate business rules."""
        from django.core.exceptions import ValidationError
        
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation."""
        self.clean()
        super().save(*args, **kwargs)