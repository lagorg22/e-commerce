from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    """
    Main order model to track customer orders
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
    
class OrderItem(models.Model):
    """
    Individual items within an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of purchase
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"
    
    class Meta:
        ordering = ['order', 'id']
