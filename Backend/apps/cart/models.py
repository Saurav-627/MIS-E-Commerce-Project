from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.products.models import Product, ProductVariant

User = get_user_model()


class Cart(BaseModel):
    """
    Shopping cart model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    session_key = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart for {self.user.email if self.user else self.session_key}"

    @property
    def total_items(self):
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def total_price(self):
        total = 0
        for item in self.items.all():
            total += item.total_price
        return total

    @property
    def is_empty(self):
        return not self.items.exists()

    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()

    def add_item(self, product, variant=None, quantity=1):
        """Add item to cart or update quantity if exists"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item

    def remove_item(self, product, variant=None):
        """Remove item from cart"""
        try:
            cart_item = CartItem.objects.get(
                cart=self,
                product=product,
                variant=variant
            )
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def update_item_quantity(self, product, variant=None, quantity=1):
        """Update item quantity"""
        try:
            cart_item = CartItem.objects.get(
                cart=self,
                product=product,
                variant=variant
            )
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return True
        except CartItem.DoesNotExist:
            return False


class CartItem(BaseModel):
    """
    Cart item model
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        variant_info = f" ({self.variant.display_name})" if self.variant else ""
        return f"{self.product.name}{variant_info} x {self.quantity}"

    @property
    def unit_price(self):
        """Get unit price (variant price if available, otherwise product price)"""
        if self.variant and self.variant.price:
            return self.variant.price
        return self.product.price

    @property
    def total_price(self):
        """Get total price for this cart item"""
        return self.unit_price * self.quantity

    @property
    def is_available(self):
        """Check if item is still available"""
        if not self.product.is_active or self.product.status != 'active':
            return False
        
        if self.variant:
            return self.variant.is_active and self.variant.stock_quantity >= self.quantity
        
        if self.product.track_inventory:
            return self.product.stock_quantity >= self.quantity
        
        return True

    def clean(self):
        """Validate cart item"""
        from django.core.exceptions import ValidationError
        
        if self.variant and self.variant.product != self.product:
            raise ValidationError("Variant must belong to the selected product")
        
        if not self.is_available:
            raise ValidationError("Product is not available in the requested quantity")


class WishlistItem(BaseModel):
    """
    Wishlist item model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'wishlist_items'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['user', 'product', 'variant']

    def __str__(self):
        variant_info = f" ({self.variant.display_name})" if self.variant else ""
        return f"{self.product.name}{variant_info} - {self.user.email}"

    @property
    def is_available(self):
        """Check if wishlist item is still available"""
        if not self.product.is_active or self.product.status != 'active':
            return False
        
        if self.variant:
            return self.variant.is_active
        
        return True