from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, WishlistItem
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, WishlistItemSerializer, AddToWishlistSerializer
)


class CartView(generics.RetrieveAPIView):
    """
    Get user's cart
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    """
    Add item to cart
    """
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        product = serializer.validated_data['product']
        variant = serializer.validated_data.get('variant')
        quantity = serializer.validated_data['quantity']
        
        # Check stock availability
        if variant:
            if variant.stock_quantity < quantity:
                return Response(
                    {'error': 'Insufficient stock for this variant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif product.track_inventory and product.stock_quantity < quantity:
            return Response(
                {'error': 'Insufficient stock for this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item = cart.add_item(product, variant, quantity)
        
        return Response({
            'message': 'Item added to cart successfully',
            'cart_item': CartItemSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Update cart item quantity
    """
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
        is_active=True
    )
    
    serializer = UpdateCartItemSerializer(data=request.data)
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        
        if quantity == 0:
            cart_item.delete()
            return Response({
                'message': 'Item removed from cart'
            }, status=status.HTTP_200_OK)
        
        # Check stock availability
        if cart_item.variant:
            if cart_item.variant.stock_quantity < quantity:
                return Response(
                    {'error': 'Insufficient stock for this variant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif cart_item.product.track_inventory and cart_item.product.stock_quantity < quantity:
            return Response(
                {'error': 'Insufficient stock for this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'message': 'Cart item updated successfully',
            'cart_item': CartItemSerializer(cart_item).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, item_id):
    """
    Remove item from cart
    """
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
        is_active=True
    )
    
    cart_item.delete()
    
    return Response({
        'message': 'Item removed from cart successfully'
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    """
    Clear all items from cart
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart.clear()
        return Response({
            'message': 'Cart cleared successfully'
        }, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({
            'message': 'Cart is already empty'
        }, status=status.HTTP_200_OK)


class WishlistView(generics.ListAPIView):
    """
    Get user's wishlist
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_wishlist(request):
    """
    Add item to wishlist
    """
    serializer = AddToWishlistSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.validated_data['product']
        variant = serializer.validated_data.get('variant')
        
        # Check if item already exists in wishlist
        if WishlistItem.objects.filter(
            user=request.user,
            product=product,
            variant=variant,
            is_active=True
        ).exists():
            return Response(
                {'error': 'Item already in wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wishlist_item = WishlistItem.objects.create(
            user=request.user,
            product=product,
            variant=variant
        )
        
        return Response({
            'message': 'Item added to wishlist successfully',
            'wishlist_item': WishlistItemSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_wishlist(request, item_id):
    """
    Remove item from wishlist
    """
    wishlist_item = get_object_or_404(
        WishlistItem,
        id=item_id,
        user=request.user,
        is_active=True
    )
    
    wishlist_item.delete()
    
    return Response({
        'message': 'Item removed from wishlist successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def move_to_cart(request, item_id):
    """
    Move item from wishlist to cart
    """
    wishlist_item = get_object_or_404(
        WishlistItem,
        id=item_id,
        user=request.user,
        is_active=True
    )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item already exists in cart
    if CartItem.objects.filter(
        cart=cart,
        product=wishlist_item.product,
        variant=wishlist_item.variant,
        is_active=True
    ).exists():
        return Response(
            {'error': 'Item already in cart'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add to cart
    cart_item = cart.add_item(wishlist_item.product, wishlist_item.variant, 1)
    
    # Remove from wishlist
    wishlist_item.delete()
    
    return Response({
        'message': 'Item moved to cart successfully',
        'cart_item': CartItemSerializer(cart_item).data
    }, status=status.HTTP_200_OK)