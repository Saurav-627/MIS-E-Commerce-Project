from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.permissions import IsOwner
from apps.orders.models import Order
from .models import Payment, PaymentMethod, PaymentRefund
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer, CreatePaymentMethodSerializer,
    ProcessPaymentSerializer, PaymentRefundSerializer, CreateRefundSerializer
)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Payment viewset - read only for customers
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user, is_active=True)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    Payment method viewset
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePaymentMethodSerializer
        return PaymentMethodSerializer

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default"""
        payment_method = self.get_object()
        
        # Remove default from other payment methods
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set this as default
        payment_method.is_default = True
        payment_method.save()
        
        return Response({
            'message': 'Payment method set as default'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment(request):
    """
    Process payment for an order
    """
    serializer = ProcessPaymentSerializer(data=request.data)
    if serializer.is_valid():
        order_id = serializer.validated_data['order_id']
        payment_method = serializer.validated_data['payment_method']
        
        # Get order
        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user,
                is_active=True
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order is already paid
        if order.is_paid:
            return Response(
                {'error': 'Order is already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=payment_method,
            amount=order.total_amount,
            status='processing'
        )
        
        # Process payment based on method
        if payment_method == 'cash_on_delivery':
            # For COD, mark as pending
            payment.status = 'pending'
            payment.save()
            
            # Update order payment status
            order.payment_status = 'pending'
            order.save()
            
            return Response({
                'message': 'Order placed successfully with Cash on Delivery',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_201_CREATED)
        
        elif payment_method in ['credit_card', 'debit_card']:
            # For card payments, integrate with payment gateway
            # This is a simplified mock implementation
            
            try:
                # Mock payment processing
                # In production, integrate with Stripe, PayPal, etc.
                success = mock_process_card_payment(payment, serializer.validated_data)
                
                if success:
                    payment.status = 'completed'
                    payment.transaction_id = f"txn_{payment.id}"
                    payment.save()
                    
                    # Update order payment status
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    order.save()
                    
                    return Response({
                        'message': 'Payment processed successfully',
                        'payment': PaymentSerializer(payment).data
                    }, status=status.HTTP_201_CREATED)
                else:
                    payment.status = 'failed'
                    payment.save()
                    
                    return Response(
                        {'error': 'Payment processing failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Exception as e:
                payment.status = 'failed'
                payment.save()
                
                return Response(
                    {'error': 'Payment processing error'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        else:
            return Response(
                {'error': 'Payment method not supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_refund(request):
    """
    Create refund for a payment (admin only)
    """
    serializer = CreateRefundSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.validated_data['payment_id']
        amount = serializer.validated_data['amount']
        reason = serializer.validated_data.get('reason', '')
        
        try:
            refund = payment.process_refund(amount, reason)
            refund.processed_by = request.user
            refund.save()
            
            # Mock refund processing
            # In production, integrate with payment gateway
            success = mock_process_refund(refund)
            
            if success:
                refund.status = 'completed'
                refund.refund_transaction_id = f"refund_{refund.id}"
                refund.save()
                
                return Response({
                    'message': 'Refund processed successfully',
                    'refund': PaymentRefundSerializer(refund).data
                }, status=status.HTTP_201_CREATED)
            else:
                refund.status = 'failed'
                refund.save()
                
                return Response(
                    {'error': 'Refund processing failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def mock_process_card_payment(payment, payment_data):
    """
    Mock card payment processing
    In production, integrate with actual payment gateway
    """
    import random
    
    # Simulate payment processing
    # 90% success rate for demo purposes
    return random.random() > 0.1


def mock_process_refund(refund):
    """
    Mock refund processing
    In production, integrate with actual payment gateway
    """
    import random
    
    # Simulate refund processing
    # 95% success rate for demo purposes
    return random.random() > 0.05


# Webhook endpoints for payment gateways
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """
    Stripe webhook endpoint
    """
    # In production, verify webhook signature
    # Process webhook events
    
    from .models import PaymentWebhook
    
    # Store webhook for processing
    webhook = PaymentWebhook.objects.create(
        gateway='stripe',
        event_type=request.data.get('type', 'unknown'),
        event_id=request.data.get('id', ''),
        payload=request.data,
        headers=dict(request.headers)
    )
    
    # Process webhook asynchronously
    # process_stripe_webhook.delay(webhook.id)
    
    return Response({'received': True}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def paypal_webhook(request):
    """
    PayPal webhook endpoint
    """
    # Similar to Stripe webhook
    from .models import PaymentWebhook
    
    webhook = PaymentWebhook.objects.create(
        gateway='paypal',
        event_type=request.data.get('event_type', 'unknown'),
        event_id=request.data.get('id', ''),
        payload=request.data,
        headers=dict(request.headers)
    )
    
    return Response({'received': True}, status=status.HTTP_200_OK)