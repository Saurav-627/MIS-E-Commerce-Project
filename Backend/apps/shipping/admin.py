from django.contrib import admin
from .models import (
    ShippingMethod, ShippingZone, ShippingZoneMethod, Shipment,
    ShipmentTracking, ShippingLabel, ShippingRate
)


class ShippingZoneMethodInline(admin.TabularInline):
    model = ShippingZoneMethod
    extra = 1
    fields = [
        'method', 'base_cost_override', 'cost_per_kg_override',
        'free_shipping_threshold_override'
    ]


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'carrier', 'base_cost', 'cost_per_kg',
        'delivery_estimate', 'is_express', 'is_international', 'is_active'
    ]
    list_filter = [
        'carrier', 'is_express', 'is_international', 'is_active', 'created_at'
    ]
    search_fields = ['name', 'description', 'carrier']
    readonly_fields = ['delivery_estimate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'carrier')
        }),
        ('Pricing', {
            'fields': ('base_cost', 'cost_per_kg', 'free_shipping_threshold')
        }),
        ('Delivery', {
            'fields': ('min_delivery_days', 'max_delivery_days', 'delivery_estimate')
        }),
        ('Features', {
            'fields': ('is_express', 'is_international')
        }),
        ('Restrictions', {
            'fields': ('max_weight', 'restricted_countries'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [ShippingZoneMethodInline]


class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    fields = ['status', 'location', 'description', 'event_time']
    readonly_fields = ['created_at']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_number', 'order', 'shipping_method', 'status',
        'shipped_at', 'estimated_delivery', 'delivered_at', 'created_at'
    ]
    list_filter = [
        'status', 'shipping_method', 'signature_required',
        'shipped_at', 'delivered_at', 'created_at'
    ]
    search_fields = [
        'tracking_number', 'order__order_number', 'order__user__email'
    ]
    readonly_fields = [
        'tracking_number', 'is_delivered', 'is_in_transit',
        'can_be_cancelled', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Shipment Information', {
            'fields': ('order', 'shipping_method', 'tracking_number', 'carrier_tracking_url')
        }),
        ('Status', {
            'fields': ('status', 'is_delivered', 'is_in_transit', 'can_be_cancelled')
        }),
        ('Physical Details', {
            'fields': ('weight', 'dimensions', 'signature_required', 'insurance_value')
        }),
        ('Addresses', {
            'fields': ('pickup_address', 'delivery_address'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('shipped_at', 'estimated_delivery', 'delivered_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ShipmentTrackingInline]
    
    actions = ['mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='picked_up', shipped_at=timezone.now())
        self.message_user(request, f'{queryset.count()} shipments marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected shipments as shipped'
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{queryset.count()} shipments marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected shipments as delivered'


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = [
        'shipment', 'status', 'location', 'event_time', 'created_at'
    ]
    list_filter = ['status', 'event_time', 'created_at']
    search_fields = [
        'shipment__tracking_number', 'location', 'description'
    ]
    readonly_fields = ['created_at']


@admin.register(ShippingLabel)
class ShippingLabelAdmin(admin.ModelAdmin):
    list_display = [
        'shipment', 'label_format', 'postage_cost', 'is_printed',
        'printed_at', 'created_at'
    ]
    list_filter = [
        'label_format', 'is_printed', 'printed_at', 'created_at'
    ]
    search_fields = [
        'shipment__tracking_number', 'carrier_label_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_printed']
    
    def mark_as_printed(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_printed=True, printed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} labels marked as printed.')
    mark_as_printed.short_description = 'Mark selected labels as printed'


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = [
        'shipping_method', 'origin_country', 'destination_country',
        'weight_from', 'weight_to', 'rate', 'expires_at', 'is_expired'
    ]
    list_filter = [
        'shipping_method', 'origin_country', 'destination_country',
        'expires_at', 'created_at'
    ]
    search_fields = [
        'shipping_method__name', 'origin_country', 'destination_country'
    ]
    readonly_fields = ['is_expired', 'created_at', 'updated_at']