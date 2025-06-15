from rest_framework import serializers
from .models import (
    ShippingMethod, ShippingZone, Shipment, ShipmentTracking, ShippingLabel
)


class ShippingMethodSerializer(serializers.ModelSerializer):
    """
    Shipping method serializer
    """
    delivery_estimate = serializers.CharField(read_only=True)

    class Meta:
        model = ShippingMethod
        fields = [
            'id', 'name', 'description', 'carrier', 'base_cost',
            'cost_per_kg', 'free_shipping_threshold', 'min_delivery_days',
            'max_delivery_days', 'delivery_estimate', 'is_express',
            'is_international', 'max_weight'
        ]


class ShippingZoneSerializer(serializers.ModelSerializer):
    """
    Shipping zone serializer
    """
    shipping_methods = ShippingMethodSerializer(many=True, read_only=True)

    class Meta:
        model = ShippingZone
        fields = ['id', 'name', 'countries', 'shipping_methods']


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    """
    Shipment tracking serializer
    """
    class Meta:
        model = ShipmentTracking
        fields = [
            'id', 'status', 'location', 'description', 'event_time',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ShipmentSerializer(serializers.ModelSerializer):
    """
    Shipment serializer
    """
    shipping_method = ShippingMethodSerializer(read_only=True)
    tracking_events = ShipmentTrackingSerializer(many=True, read_only=True)
    is_delivered = serializers.BooleanField(read_only=True)
    is_in_transit = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'shipping_method', 'tracking_number',
            'carrier_tracking_url', 'status', 'weight', 'dimensions',
            'delivery_address', 'shipped_at', 'estimated_delivery',
            'delivered_at', 'notes', 'signature_required',
            'insurance_value', 'tracking_events', 'is_delivered',
            'is_in_transit', 'can_be_cancelled', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tracking_number', 'created_at', 'updated_at'
        ]


class ShippingLabelSerializer(serializers.ModelSerializer):
    """
    Shipping label serializer
    """
    class Meta:
        model = ShippingLabel
        fields = [
            'id', 'shipment', 'label_format', 'label_url',
            'postage_cost', 'insurance_cost', 'is_printed',
            'printed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'label_url', 'postage_cost', 'insurance_cost',
            'is_printed', 'printed_at', 'created_at'
        ]


class CalculateShippingSerializer(serializers.Serializer):
    """
    Calculate shipping rates serializer
    """
    destination_country = serializers.CharField(max_length=2, default='US')
    destination_state = serializers.CharField(max_length=100, required=False)
    destination_city = serializers.CharField(max_length=100, required=False)
    destination_postal_code = serializers.CharField(max_length=20, required=False)
    weight = serializers.DecimalField(max_digits=8, decimal_places=2, default=1.0)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)


class CreateShipmentSerializer(serializers.Serializer):
    """
    Create shipment serializer
    """
    order_id = serializers.UUIDField()
    shipping_method_id = serializers.UUIDField()
    weight = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    dimensions = serializers.JSONField(required=False)
    signature_required = serializers.BooleanField(default=False)
    insurance_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_order_id(self, value):
        from apps.orders.models import Order
        try:
            order = Order.objects.get(id=value, is_active=True)
            if hasattr(order, 'shipment'):
                raise serializers.ValidationError("Order already has a shipment")
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")

    def validate_shipping_method_id(self, value):
        try:
            method = ShippingMethod.objects.get(id=value, is_active=True)
            return method
        except ShippingMethod.DoesNotExist:
            raise serializers.ValidationError("Shipping method not found")


class TrackShipmentSerializer(serializers.Serializer):
    """
    Track shipment serializer
    """
    tracking_number = serializers.CharField(max_length=100)

    def validate_tracking_number(self, value):
        try:
            shipment = Shipment.objects.get(tracking_number=value, is_active=True)
            return shipment
        except Shipment.DoesNotExist:
            raise serializers.ValidationError("Shipment not found")