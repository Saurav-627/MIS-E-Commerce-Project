from django.contrib import admin
from .models import Payment, PaymentMethod, PaymentRefund, PaymentWebhook


class PaymentRefundInline(admin.TabularInline):
    model = PaymentRefund
    extra = 0
    fields = ['amount', 'reason', 'status', 'processed_at', 'processed_by']
    readonly_fields = ['processed_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order', 'user', 'payment_method', 'amount', 'status',
        'transaction_id', 'processed_at', 'created_at'
    ]
    list_filter = [
        'payment_method', 'status', 'currency', 'processed_at', 'created_at'
    ]
    search_fields = [
        'order__order_number', 'user__email', 'transaction_id'
    ]
    readonly_fields = [
        'is_successful', 'can_be_refunded', 'remaining_refund_amount',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'user', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'gateway_response', 'processed_at')
        }),
        ('Refund Information', {
            'fields': ('refund_amount', 'refund_reason', 'remaining_refund_amount'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PaymentRefundInline]
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', processed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} payments marked as completed.')
    mark_as_completed.short_description = 'Mark selected payments as completed'
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f'{queryset.count()} payments marked as failed.')
    mark_as_failed.short_description = 'Mark selected payments as failed'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'card_type', 'masked_number', 'cardholder_name',
        'is_default', 'is_verified', 'is_expired', 'created_at'
    ]
    list_filter = [
        'card_type', 'is_default', 'is_verified', 'expiry_year', 'created_at'
    ]
    search_fields = [
        'user__email', 'cardholder_name', 'last_four_digits'
    ]
    readonly_fields = ['masked_number', 'is_expired', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Card Information', {
            'fields': ('user', 'card_type', 'last_four_digits', 'masked_number', 'cardholder_name')
        }),
        ('Expiry', {
            'fields': ('expiry_month', 'expiry_year', 'is_expired')
        }),
        ('Settings', {
            'fields': ('is_default', 'is_verified', 'gateway_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'payment', 'amount', 'status', 'processed_at',
        'processed_by', 'created_at'
    ]
    list_filter = ['status', 'processed_at', 'created_at']
    search_fields = [
        'payment__order__order_number', 'payment__transaction_id',
        'refund_transaction_id', 'reason'
    ]
    readonly_fields = ['is_successful', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Transaction Details', {
            'fields': ('refund_transaction_id', 'gateway_response')
        }),
        ('Processing Information', {
            'fields': ('processed_at', 'processed_by', 'is_successful')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'gateway', 'event_type', 'event_id', 'processed',
        'processed_at', 'created_at'
    ]
    list_filter = ['gateway', 'event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'gateway', 'event_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Webhook Information', {
            'fields': ('gateway', 'event_type', 'event_id')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at', 'error_message')
        }),
        ('Data', {
            'fields': ('payload', 'headers'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processed']
    
    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        queryset.update(processed=True, processed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} webhooks marked as processed.')
    mark_as_processed.short_description = 'Mark selected webhooks as processed'