from rest_framework import serializers
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer
from .models import Cart, CartItem, WishlistItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Cart item serializer
    """
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity', 'unit_price',
            'total_price', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    """
    Cart serializer
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_empty = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'total_items', 'total_price', 'is_empty',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """
    Add to cart serializer
    """
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        from apps.products.models import Product, ProductVariant
        
        try:
            product = Product.objects.get(id=attrs['product_id'], is_active=True)
            attrs['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        variant_id = attrs.get('variant_id')
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                    is_active=True
                )
                attrs['variant'] = variant
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found")
        else:
            attrs['variant'] = None
        
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Update cart item serializer
    """
    quantity = serializers.IntegerField(min_value=0)


class WishlistItemSerializer(serializers.ModelSerializer):
    """
    Wishlist item serializer
    """
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = WishlistItem
        fields = [
            'id', 'product', 'variant', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddToWishlistSerializer(serializers.Serializer):
    """
    Add to wishlist serializer
    """
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        from apps.products.models import Product, ProductVariant
        
        try:
            product = Product.objects.get(id=attrs['product_id'], is_active=True)
            attrs['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        variant_id = attrs.get('variant_id')
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                    is_active=True
                )
                attrs['variant'] = variant
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found")
        else:
            attrs['variant'] = None
        
        return attrs