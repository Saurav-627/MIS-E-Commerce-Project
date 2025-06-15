from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.orders.models import Order

User = get_user_model()


class ShippingMethod(BaseModel):
    """
    Shipping method model
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    carrier = models.CharField(max_length=50)  # UPS, FedEx, DHL, etc.
    
    # Pricing
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Delivery estimates
    min_delivery_days = models.PositiveIntegerField()
    max_delivery_days = models.PositiveIntegerField()
    
    # Availability
    is_express = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    
    # Restrictions
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    restricted_countries = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'shipping_methods'
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'

    def __str__(self):
        return f"{self.name} ({self.carrier})"

    def calculate_cost(self, weight=0, order_total=0, destination_country='US'):
        """Calculate shipping cost based on weight and order total"""
        # Check if free shipping applies
        if self.free_shipping_threshold and order_total >= self.free_shipping_threshold:
            return 0
        
        # Check country restrictions
        if destination_country in self.restricted_countries:
            return None  # Not available for this country
        
        # Check weight restrictions
        if self.max_weight and weight > self.max_weight:
            return None  # Exceeds weight limit
        
        # Calculate cost
        cost = self.base_cost + (weight * self.cost_per_kg)
        return cost

    @property
    def delivery_estimate(self):
        if self.min_delivery_days == self.max_delivery_days:
            return f"{self.min_delivery_days} days"
        return f"{self.min_delivery_days}-{self.max_delivery_days} days"


class ShippingZone(BaseModel):
    """
    Shipping zone model for different regions
    """
    name = models.CharField(max_length=100)
    countries = models.JSONField()  # List of country codes
    shipping_methods = models.ManyToManyField(ShippingMethod, through='ShippingZoneMethod')

    class Meta:
        db_table = 'shipping_zones'
        verbose_name = 'Shipping Zone'
        verbose_name_plural = 'Shipping Zones'

    def __str__(self):
        return self.name

    def is_country_in_zone(self, country_code):
        return country_code in self.countries


class ShippingZoneMethod(BaseModel):
    """
    Shipping zone method relationship with custom pricing
    """
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE)
    method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    
    # Zone-specific pricing overrides
    base_cost_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_per_kg_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    free_shipping_threshold_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'shipping_zone_methods'
        verbose_name = 'Shipping Zone Method'
        verbose_name_plural = 'Shipping Zone Methods'
        unique_together = ['zone', 'method']

    def __str__(self):
        return f"{self.zone.name} - {self.method.name}"

    def calculate_cost(self, weight=0, order_total=0):
        """Calculate cost using zone-specific overrides if available"""
        base_cost = self.base_cost_override or self.method.base_cost
        cost_per_kg = self.cost_per_kg_override or self.method.cost_per_kg
        free_threshold = self.free_shipping_threshold_override or self.method.free_shipping_threshold
        
        # Check if free shipping applies
        if free_threshold and order_total >= free_threshold:
            return 0
        
        # Calculate cost
        cost = base_cost + (weight * cost_per_kg)
        return cost


class Shipment(BaseModel):
    """
    Shipment model for tracking deliveries
    """
    SHIPMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed_delivery', 'Failed Delivery'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    
    # Tracking information
    tracking_number = models.CharField(max_length=100, unique=True)
    carrier_tracking_url = models.URLField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES, default='pending')
    
    # Shipping details
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.JSONField(blank=True, null=True)  # {length, width, height}
    
    # Addresses (copied from order for tracking history)
    pickup_address = models.JSONField(blank=True, null=True)
    delivery_address = models.JSONField()
    
    # Dates
    shipped_at = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    signature_required = models.BooleanField(default=False)
    insurance_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'shipments'
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment {self.tracking_number} - Order {self.order.order_number}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)

    def generate_tracking_number(self):
        """Generate unique tracking number"""
        import random
        import string
        
        while True:
            tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            if not Shipment.objects.filter(tracking_number=tracking_number).exists():
                return tracking_number

    @property
    def is_delivered(self):
        return self.status == 'delivered'

    @property
    def is_in_transit(self):
        return self.status in ['picked_up', 'in_transit', 'out_for_delivery']

    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'picked_up']


class ShipmentTracking(BaseModel):
    """
    Shipment tracking events
    """
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=20, choices=Shipment.SHIPMENT_STATUS_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    event_time = models.DateTimeField()
    
    # Additional tracking data from carrier
    carrier_data = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'shipment_tracking'
        verbose_name = 'Shipment Tracking'
        verbose_name_plural = 'Shipment Tracking'
        ordering = ['-event_time']

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} at {self.event_time}"


class ShippingLabel(BaseModel):
    """
    Shipping label model
    """
    LABEL_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('png', 'PNG'),
        ('zpl', 'ZPL'),
        ('epl', 'EPL'),
    ]

    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='label')
    
    # Label details
    label_format = models.CharField(max_length=10, choices=LABEL_FORMAT_CHOICES, default='pdf')
    label_url = models.URLField(blank=True)
    label_data = models.TextField(blank=True)  # Base64 encoded label data
    
    # Carrier response
    carrier_label_id = models.CharField(max_length=100, blank=True)
    carrier_response = models.JSONField(blank=True, null=True)
    
    # Costs
    postage_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_printed = models.BooleanField(default=False)
    printed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'shipping_labels'
        verbose_name = 'Shipping Label'
        verbose_name_plural = 'Shipping Labels'

    def __str__(self):
        return f"Label for {self.shipment.tracking_number}"

    def mark_as_printed(self):
        from django.utils import timezone
        self.is_printed = True
        self.printed_at = timezone.now()
        self.save()


class ShippingRate(BaseModel):
    """
    Cached shipping rates for quick lookup
    """
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    origin_country = models.CharField(max_length=2)
    destination_country = models.CharField(max_length=2)
    weight_from = models.DecimalField(max_digits=8, decimal_places=2)
    weight_to = models.DecimalField(max_digits=8, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Cache expiry
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'shipping_rates'
        verbose_name = 'Shipping Rate'
        verbose_name_plural = 'Shipping Rates'
        unique_together = [
            'shipping_method', 'origin_country', 'destination_country',
            'weight_from', 'weight_to'
        ]

    def __str__(self):
        return f"{self.shipping_method.name} - {self.origin_country} to {self.destination_country}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at