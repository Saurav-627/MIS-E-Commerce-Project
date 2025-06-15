from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.permissions import IsOwner
from .models import (
    ShippingMethod, ShippingZone, Shipment, ShipmentTracking, ShippingLabel
)
from .serializers import (
    ShippingMethodSerializer, ShippingZoneSerializer, ShipmentSerializer,
    ShipmentTrackingSerializer, ShippingLabelSerializer,
    CalculateShippingSerializer, CreateShipmentSerializer, TrackShipmentSerializer
)


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shipping method viewset - read only
    """
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]


class ShippingZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shipping zone viewset - read only
    """
    queryset = ShippingZone.objects.filter(is_active=True)
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.AllowAny]


class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shipment viewset - read only for customers
    """
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(
            order__user=self.request.user,
            is_active=True
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a shipment"""
        shipment = self.get_object()
        
        if not shipment.can_be_cancelled:
            return Response(
                {'error': 'Shipment cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shipment.status = 'cancelled'
        shipment.save()
        
        # Create tracking event
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='cancelled',
            description='Shipment cancelled by customer',
            event_time=timezone.now()
        )
        
        return Response({
            'message': 'Shipment cancelled successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def calculate_shipping(request):
    """
    Calculate shipping rates for given parameters
    """
    serializer = CalculateShippingSerializer(data=request.data)
    if serializer.is_valid():
        destination_country = serializer.validated_data['destination_country']
        weight = serializer.validated_data['weight']
        order_total = serializer.validated_data['order_total']
        
        # Get available shipping methods for destination
        available_methods = []
        
        # Find shipping zone for destination country
        zones = ShippingZone.objects.filter(
            countries__contains=[destination_country],
            is_active=True
        )
        
        if zones.exists():
            zone = zones.first()
            for zone_method in zone.shippingzonemethod_set.filter(is_active=True):
                method = zone_method.method
                if method.is_active:
                    cost = zone_method.calculate_cost(weight, order_total)
                    if cost is not None:
                        available_methods.append({
                            'id': method.id,
                            'name': method.name,
                            'description': method.description,
                            'carrier': method.carrier,
                            'cost': cost,
                            'delivery_estimate': method.delivery_estimate,
                            'is_express': method.is_express
                        })
        else:
            # Fallback to default methods
            methods = ShippingMethod.objects.filter(is_active=True)
            for method in methods:
                cost = method.calculate_cost(weight, order_total, destination_country)
                if cost is not None:
                    available_methods.append({
                        'id': method.id,
                        'name': method.name,
                        'description': method.description,
                        'carrier': method.carrier,
                        'cost': cost,
                        'delivery_estimate': method.delivery_estimate,
                        'is_express': method.is_express
                    })
        
        # Sort by cost
        available_methods.sort(key=lambda x: x['cost'])
        
        return Response({
            'destination_country': destination_country,
            'weight': weight,
            'order_total': order_total,
            'shipping_methods': available_methods
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_shipment(request):
    """
    Create shipment for an order (admin only)
    """
    serializer = CreateShipmentSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.validated_data['order_id']
        shipping_method = serializer.validated_data['shipping_method_id']
        
        # Create shipment
        shipment = Shipment.objects.create(
            order=order,
            shipping_method=shipping_method,
            weight=serializer.validated_data.get('weight'),
            dimensions=serializer.validated_data.get('dimensions'),
            signature_required=serializer.validated_data.get('signature_required', False),
            insurance_value=serializer.validated_data.get('insurance_value'),
            notes=serializer.validated_data.get('notes', ''),
            delivery_address=order.shipping_address
        )
        
        # Create initial tracking event
        from django.utils import timezone
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='pending',
            description='Shipment created',
            event_time=timezone.now()
        )
        
        # Update order status
        order.status = 'processing'
        order.tracking_number = shipment.tracking_number
        order.save()
        
        return Response({
            'message': 'Shipment created successfully',
            'shipment': ShipmentSerializer(shipment).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_shipment(request):
    """
    Track shipment by tracking number
    """
    serializer = TrackShipmentSerializer(data=request.data)
    if serializer.is_valid():
        shipment = serializer.validated_data['tracking_number']
        
        return Response({
            'shipment': ShipmentSerializer(shipment).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_tracking(request, shipment_id):
    """
    Update shipment tracking (admin only)
    """
    shipment = get_object_or_404(Shipment, id=shipment_id, is_active=True)
    
    status_value = request.data.get('status')
    location = request.data.get('location', '')
    description = request.data.get('description', '')
    
    if not status_value:
        return Response(
            {'error': 'Status is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status
    valid_statuses = [choice[0] for choice in Shipment.SHIPMENT_STATUS_CHOICES]
    if status_value not in valid_statuses:
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update shipment status
    shipment.status = status_value
    
    # Set timestamps based on status
    from django.utils import timezone
    now = timezone.now()
    
    if status_value == 'picked_up' and not shipment.shipped_at:
        shipment.shipped_at = now
    elif status_value == 'delivered' and not shipment.delivered_at:
        shipment.delivered_at = now
    
    shipment.save()
    
    # Create tracking event
    ShipmentTracking.objects.create(
        shipment=shipment,
        status=status_value,
        location=location,
        description=description or f"Shipment status updated to {status_value}",
        event_time=now
    )
    
    # Update order status
    if status_value == 'delivered':
        shipment.order.status = 'delivered'
        shipment.order.delivered_at = now
        shipment.order.save()
    elif status_value == 'picked_up':
        shipment.order.status = 'shipped'
        shipment.order.shipped_at = now
        shipment.order.save()
    
    return Response({
        'message': 'Tracking updated successfully',
        'shipment': ShipmentSerializer(shipment).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def generate_label(request, shipment_id):
    """
    Generate shipping label (admin only)
    """
    shipment = get_object_or_404(Shipment, id=shipment_id, is_active=True)
    
    if hasattr(shipment, 'label'):
        return Response(
            {'error': 'Label already exists for this shipment'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mock label generation
    # In production, integrate with carrier APIs
    label = ShippingLabel.objects.create(
        shipment=shipment,
        label_format='pdf',
        label_url=f"https://example.com/labels/{shipment.tracking_number}.pdf",
        postage_cost=shipment.shipping_method.base_cost,
        carrier_label_id=f"label_{shipment.tracking_number}"
    )
    
    return Response({
        'message': 'Shipping label generated successfully',
        'label': ShippingLabelSerializer(label).data
    }, status=status.HTTP_201_CREATED)