from rest_framework import serializers
from apps.products.serializers import ProductListSerializer
from apps.users.serializers import AddressSerializer
from .models import Order, OrderItem, OrderStatusHistory, Coupon, CouponUsage


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Order item serializer
    """
    product = ProductListSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'unit_price',
            'quantity', 'variant_attributes', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Order status history serializer
    """
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'status', 'notes', 'changed_by', 'changed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """
    Order list serializer (minimal fields for list views)
    """
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'total_amount',
            'total_items', 'created_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Order detail serializer (all fields for detail views)
    """
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'subtotal', 'tax_amount', 'shipping_amount',
            'discount_amount', 'total_amount', 'status', 'payment_status',
            'billing_address', 'shipping_address', 'notes', 'tracking_number',
            'items', 'status_history', 'total_items', 'can_be_cancelled',
            'is_paid', 'created_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax_amount', 'total_amount',
            'created_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """
    Create order serializer
    """
    billing_address_id = serializers.UUIDField()
    shipping_address_id = serializers.UUIDField()
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate_billing_address_id(self, value):
        from apps.users.models import Address
        try:
            address = Address.objects.get(
                id=value,
                user=self.context['request'].user,
                is_active=True
            )
            return address
        except Address.DoesNotExist:
            raise serializers.ValidationError("Invalid billing address")

    def validate_shipping_address_id(self, value):
        from apps.users.models import Address
        try:
            address = Address.objects.get(
                id=value,
                user=self.context['request'].user,
                is_active=True
            )
            return address
        except Address.DoesNotExist:
            raise serializers.ValidationError("Invalid shipping address")

    def validate_coupon_code(self, value):
        if value:
            try:
                coupon = Coupon.objects.get(code=value, is_active=True)
                if not coupon.is_valid:
                    raise serializers.ValidationError("Coupon is not valid")
                if not coupon.can_be_used_by_user(self.context['request'].user):
                    raise serializers.ValidationError("Coupon cannot be used by this user")
                return coupon
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code")
        return None


class CouponSerializer(serializers.ModelSerializer):
    """
    Coupon serializer
    """
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'minimum_amount', 'maximum_discount',
            'valid_from', 'valid_until', 'is_valid'
        ]


class ValidateCouponSerializer(serializers.Serializer):
    """
    Validate coupon serializer
    """
    code = serializers.CharField(max_length=50)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value, is_active=True)
            if not coupon.is_valid:
                raise serializers.ValidationError("Coupon is not valid")
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")