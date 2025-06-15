from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.orders.models import Order

User = get_user_model()


class Payment(BaseModel):
    """
    Payment model
    """
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # External payment gateway details
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Refund info
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - Order {self.order.order_number} - {self.status}"

    @property
    def is_successful(self):
        return self.status == 'completed'

    @property
    def can_be_refunded(self):
        return self.status == 'completed' and self.refund_amount < self.amount

    @property
    def remaining_refund_amount(self):
        return self.amount - self.refund_amount

    def process_refund(self, amount, reason=''):
        """Process a refund for this payment"""
        if not self.can_be_refunded:
            raise ValueError("Payment cannot be refunded")
        
        if amount > self.remaining_refund_amount:
            raise ValueError("Refund amount exceeds remaining amount")
        
        # Create refund record
        refund = PaymentRefund.objects.create(
            payment=self,
            amount=amount,
            reason=reason,
            status='pending'
        )
        
        # Update payment refund amount
        self.refund_amount += amount
        
        # Update payment status
        if self.refund_amount >= self.amount:
            self.status = 'refunded'
        else:
            self.status = 'partially_refunded'
        
        self.save()
        
        return refund


class PaymentMethod(BaseModel):
    """
    Saved payment methods for users
    """
    CARD_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Card details (encrypted/tokenized in production)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    last_four_digits = models.CharField(max_length=4)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    cardholder_name = models.CharField(max_length=100)
    
    # Payment gateway token (for secure storage)
    gateway_token = models.CharField(max_length=255, blank=True)
    
    # Settings
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'

    def __str__(self):
        return f"{self.card_type.title()} ending in {self.last_four_digits}"

    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        from datetime import date
        today = date.today()
        return (self.expiry_year < today.year or 
                (self.expiry_year == today.year and self.expiry_month < today.month))

    @property
    def masked_number(self):
        return f"**** **** **** {self.last_four_digits}"


class PaymentRefund(BaseModel):
    """
    Payment refund model
    """
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    
    # Gateway details
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    # Processing info
    processed_at = models.DateTimeField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'payment_refunds'
        verbose_name = 'Payment Refund'
        verbose_name_plural = 'Payment Refunds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.id} - Payment {self.payment.id} - {self.amount}"

    @property
    def is_successful(self):
        return self.status == 'completed'


class PaymentWebhook(BaseModel):
    """
    Payment webhook events from payment gateways
    """
    EVENT_TYPE_CHOICES = [
        ('payment.succeeded', 'Payment Succeeded'),
        ('payment.failed', 'Payment Failed'),
        ('payment.refunded', 'Payment Refunded'),
        ('payment.disputed', 'Payment Disputed'),
        ('payment.cancelled', 'Payment Cancelled'),
    ]

    gateway = models.CharField(max_length=50)  # stripe, paypal, etc.
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    event_id = models.CharField(max_length=100, unique=True)
    
    # Webhook data
    payload = models.JSONField()
    headers = models.JSONField(blank=True, null=True)
    
    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'payment_webhooks'
        verbose_name = 'Payment Webhook'
        verbose_name_plural = 'Payment Webhooks'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.gateway} - {self.event_type} - {self.event_id}"

    def mark_as_processed(self):
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.save()