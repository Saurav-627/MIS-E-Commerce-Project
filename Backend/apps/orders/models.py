from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.products.models import Product, ProductVariant
from apps.users.models import Address
import uuid

User = get_user_model()


class Order(BaseModel):
    """
    Order model
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Addresses (stored as JSON to preserve order history)
    billing_address = models.JSONField()
    shipping_address = models.JSONField()
    
    # Additional info
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    confirmed_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        
        while True:
            order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number

    @property
    def total_items(self):
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']

    @property
    def is_paid(self):
        return self.payment_status == 'paid'

    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        # Tax calculation (simplified - 10% tax rate)
        self.tax_amount = self.subtotal * 0.10
        # Total calculation
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total_amount'])


class OrderItem(BaseModel):
    """
    Order item model
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    
    # Product details at time of order (for historical accuracy)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    
    # Variant details (if applicable)
    variant_attributes = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.product_name} x {self.quantity} - Order {self.order.order_number}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Store product details at time of order
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.variant.sku if self.variant else self.product.sku
        if not self.unit_price:
            self.unit_price = self.variant.effective_price if self.variant else self.product.price
        
        # Store variant attributes
        if self.variant and not self.variant_attributes:
            self.variant_attributes = {
                attr.attribute.name: attr.value 
                for attr in self.variant.attributes.all()
            }
        
        super().save(*args, **kwargs)


class OrderStatusHistory(BaseModel):
    """
    Order status change history
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order.order_number} - {self.status}"


class Coupon(BaseModel):
    """
    Discount coupon model
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    used_count = models.PositiveIntegerField(default=0)
    usage_limit_per_user = models.PositiveIntegerField(blank=True, null=True)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Conditions
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Applicable products/categories
    applicable_products = models.ManyToManyField(Product, blank=True)
    # applicable_categories = models.ManyToManyField(Category, blank=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (not self.usage_limit or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, amount):
        """Calculate discount amount for given order amount"""
        if not self.is_valid:
            return 0
        
        if self.minimum_amount and amount < self.minimum_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / 100)
        else:
            discount = self.discount_value
        
        if self.maximum_discount:
            discount = min(discount, self.maximum_discount)
        
        return discount

    def can_be_used_by_user(self, user):
        """Check if coupon can be used by specific user"""
        if not self.is_valid:
            return False
        
        if self.usage_limit_per_user:
            user_usage = CouponUsage.objects.filter(
                coupon=self,
                user=user
            ).count()
            return user_usage < self.usage_limit_per_user
        
        return True


class CouponUsage(BaseModel):
    """
    Coupon usage tracking
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'coupon_usages'
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'

    def __str__(self):
        return f"{self.coupon.code} used by {self.user.email} - Order {self.order.order_number}"