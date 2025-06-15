from rest_framework import serializers
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, Review
)


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer
    """
    children = serializers.SerializerMethodField()
    full_path = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'parent',
            'is_featured', 'full_path', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class BrandSerializer(serializers.ModelSerializer):
    """
    Brand serializer
    """
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Product image serializer
    """
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'is_primary', 'sort_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """
    Product attribute value serializer
    """
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value', 'slug']
        read_only_fields = ['id', 'slug']


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Product variant serializer
    """
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    display_name = serializers.CharField(read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'price', 'compare_price', 'stock_quantity',
            'weight', 'image', 'attributes', 'display_name', 'effective_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Review serializer
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'user_name', 'user_email', 'rating',
            'title', 'comment', 'is_verified_purchase', 'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """
    Product list serializer (minimal fields for list views)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'compare_price',
            'category_name', 'brand_name', 'primary_image', 'is_featured',
            'is_on_sale', 'discount_percentage', 'is_in_stock', 'average_rating',
            'review_count', 'created_at'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Product detail serializer (all fields for detail views)
    """
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    
    # Computed fields
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_name', 'category', 'brand', 'name', 'slug',
            'description', 'short_description', 'price', 'compare_price', 'cost_price',
            'sku', 'stock_quantity', 'low_stock_threshold', 'track_inventory',
            'weight', 'length', 'width', 'height', 'meta_title', 'meta_description',
            'status', 'is_featured', 'is_digital', 'requires_shipping',
            'average_rating', 'review_count', 'images', 'variants', 'reviews',
            'is_on_sale', 'discount_percentage', 'is_in_stock', 'is_low_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'seller', 'slug', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Product create/update serializer
    """
    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'name', 'description', 'short_description',
            'price', 'compare_price', 'cost_price', 'sku', 'stock_quantity',
            'low_stock_threshold', 'track_inventory', 'weight', 'length',
            'width', 'height', 'meta_title', 'meta_description', 'status',
            'is_featured', 'is_digital', 'requires_shipping'
        ]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)