from django.contrib import admin
from .models import Cart, CartItem, WishlistItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'variant', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['unit_price', 'total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['total_items', 'total_price', 'created_at', 'updated_at']
    
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['cart__user__email', 'product__name']
    readonly_fields = ['unit_price', 'total_price', 'created_at', 'updated_at']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'variant', 'is_available', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['is_available', 'created_at', 'updated_at']