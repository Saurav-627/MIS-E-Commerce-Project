from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, Coupon, CouponUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'variant', 'product_name', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    fields = ['status', 'notes', 'changed_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 'total_amount',
        'total_items', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'created_at', 'confirmed_at',
        'shipped_at', 'delivered_at'
    ]
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'order_number', 'subtotal', 'tax_amount', 'total_amount',
        'total_items', 'can_be_cancelled', 'is_paid', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        ('Addresses', {
            'fields': ('billing_address', 'shipping_address'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'tracking_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='confirmed', confirmed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} orders marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected orders as confirmed'
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product_name', 'product_sku', 'quantity',
        'unit_price', 'total_price', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['total_price', 'created_at', 'updated_at']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['created_at']


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    fields = ['user', 'order', 'discount_amount', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'discount_type', 'discount_value',
        'used_count', 'usage_limit', 'valid_from', 'valid_until', 'is_valid'
    ]
    list_filter = [
        'discount_type', 'valid_from', 'valid_until', 'is_active', 'created_at'
    ]
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['used_count', 'is_valid', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_products']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Discount Settings', {
            'fields': ('discount_type', 'discount_value', 'maximum_discount')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'used_count', 'usage_limit_per_user')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_valid')
        }),
        ('Conditions', {
            'fields': ('minimum_amount', 'applicable_products'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CouponUsageInline]


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['coupon__code', 'user__email', 'order__order_number']
    readonly_fields = ['created_at']