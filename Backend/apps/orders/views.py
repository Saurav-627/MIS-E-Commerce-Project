from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.core.permissions import IsOwner
from apps.core.pagination import StandardResultsSetPagination
from apps.cart.models import Cart
from .models import Order, OrderItem, OrderStatusHistory, Coupon
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer,
    CouponSerializer, ValidateCouponSerializer
)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Order viewset - read only for customers
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes='Cancelled by customer',
            changed_by=request.user
        )
        
        return Response({
            'message': 'Order cancelled successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    """
    Create order from cart
    """
    serializer = CreateOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            cart = Cart.objects.get(user=request.user)
            if cart.is_empty:
                return Response(
                    {'error': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Get validated data
            billing_address = serializer.validated_data['billing_address_id']
            shipping_address = serializer.validated_data['shipping_address_id']
            coupon = serializer.validated_data.get('coupon_code')
            notes = serializer.validated_data.get('notes', '')
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                billing_address={
                    'first_name': billing_address.first_name,
                    'last_name': billing_address.last_name,
                    'company': billing_address.company,
                    'address_line_1': billing_address.address_line_1,
                    'address_line_2': billing_address.address_line_2,
                    'city': billing_address.city,
                    'state': billing_address.state,
                    'postal_code': billing_address.postal_code,
                    'country': billing_address.country,
                    'phone_number': billing_address.phone_number,
                },
                shipping_address={
                    'first_name': shipping_address.first_name,
                    'last_name': shipping_address.last_name,
                    'company': shipping_address.company,
                    'address_line_1': shipping_address.address_line_1,
                    'address_line_2': shipping_address.address_line_2,
                    'city': shipping_address.city,
                    'state': shipping_address.state,
                    'postal_code': shipping_address.postal_code,
                    'country': shipping_address.country,
                    'phone_number': shipping_address.phone_number,
                },
                notes=notes,
                subtotal=0,  # Will be calculated
                total_amount=0,  # Will be calculated
            )
            
            # Create order items from cart
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                )
            
            # Calculate order totals
            order.calculate_totals()
            
            # Apply coupon if provided
            
            if coupon:
                discount_amount = coupon.calculate_discount(order.subtotal)
                if discount_amount > 0:
                    order.discount_amount = discount_amount
                    order.total_amount -= discount_amount
                    order.save()
                    
                    # Record coupon usage
                    from .models import CouponUsage
                    CouponUsage.objects.create(
                        coupon=coupon,
                        user=request.user,
                        order=order,
                        discount_amount=discount_amount
                    )
                    
                    # Update coupon usage count
                    coupon.used_count += 1
                    coupon.save()
            
            # Create initial status history
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                notes='Order created',
                changed_by=request.user
            )
            
            # Clear cart
            cart.clear()
            
            return Response({
                'message': 'Order created successfully',
                'order': OrderDetailSerializer(order).data
            }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """
    Validate coupon code
    """
    serializer = ValidateCouponSerializer(data=request.data)
    if serializer.is_valid():
        coupon = serializer.validated_data['code']
        order_amount = serializer.validated_data['order_amount']
        
        if not coupon.can_be_used_by_user(request.user):
            return Response(
                {'error': 'Coupon cannot be used by this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        discount_amount = coupon.calculate_discount(order_amount)
        
        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': discount_amount,
            'final_amount': order_amount - discount_amount
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Coupon viewset - read only
    """
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'code'

    def get_queryset(self):
        # Only show valid coupons
        from django.utils import timezone
        now = timezone.now()
        return super().get_queryset().filter(
            valid_from__lte=now,
            valid_until__gte=now
        )