from rest_framework import generics, viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsSellerOrReadOnly, IsOwnerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, Review
)
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductImageSerializer, ProductVariantSerializer, ReviewSerializer
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category viewset - read only
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured categories"""
        featured_categories = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_categories, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Brand viewset - read only
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product viewset with full CRUD operations
    """
    queryset = Product.objects.filter(is_active=True, status='active')
    permission_classes = [IsSellerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'average_rating']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For sellers, show their own products regardless of status
        if self.request.user.is_authenticated and self.request.user.is_seller:
            if self.action in ['list', 'retrieve']:
                # Show all active products for list/detail
                return queryset
            else:
                # Show seller's own products for CRUD operations
                return Product.objects.filter(seller=self.request.user, is_active=True)
        
        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale"""
        on_sale_products = self.get_queryset().exclude(compare_price__isnull=True).filter(
            price__lt=models.F('compare_price')
        )
        page = self.paginate_queryset(on_sale_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(on_sale_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get product reviews"""
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, slug=None):
        """Add a review to a product"""
        product = self.get_object()
        
        # Check if user already reviewed this product
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Product image viewset
    """
    serializer_class = ProductImageSerializer
    permission_classes = [IsSellerOrReadOnly]

    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return ProductImage.objects.filter(
            product__slug=product_slug,
            product__is_active=True,
            is_active=True
        )

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = Product.objects.get(slug=product_slug)
        serializer.save(product=product)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Review viewset
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Review.objects.filter(user=self.request.user, is_active=True)
        return Review.objects.none()

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        reviews = self.get_queryset()
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)