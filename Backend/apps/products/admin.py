from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, Review
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'stock_quantity', 'weight']


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ['user', 'rating', 'title', 'is_approved']
    readonly_fields = ['user', 'rating', 'title']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_featured', 'is_active', 'created_at']
    list_filter = ['is_featured', 'is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'seller', 'category', 'brand', 'price', 'stock_quantity',
        'status', 'is_featured', 'average_rating', 'created_at'
    ]
    list_filter = [
        'status', 'is_featured', 'category', 'brand', 'seller',
        'is_digital', 'requires_shipping', 'created_at'
    ]
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'review_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'name', 'slug', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'brand')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold', 'track_inventory')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status & Features', {
            'fields': ('status', 'is_featured', 'is_digital', 'requires_shipping')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline, ReviewInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'slug', 'created_at']
    list_filter = ['attribute', 'created_at']
    search_fields = ['attribute__name', 'value']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'stock_quantity', 'created_at']
    list_filter = ['product', 'created_at']
    search_fields = ['product__name', 'sku']
    filter_horizontal = ['attributes']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'user', 'rating', 'title', 'is_verified_purchase',
        'is_approved', 'created_at'
    ]
    list_filter = [
        'rating', 'is_verified_purchase', 'is_approved', 'created_at'
    ]
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} reviews disapproved.')
    disapprove_reviews.short_description = 'Disapprove selected reviews'