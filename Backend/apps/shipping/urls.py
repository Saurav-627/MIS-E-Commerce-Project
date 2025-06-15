from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'shipping'

router = DefaultRouter()
router.register(r'methods', views.ShippingMethodViewSet)
router.register(r'zones', views.ShippingZoneViewSet)
router.register(r'shipments', views.ShipmentViewSet, basename='shipment')

urlpatterns = [
    path('', include(router.urls)),
    path('calculate/', views.calculate_shipping, name='calculate_shipping'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('track/', views.track_shipment, name='track_shipment'),
    path('shipments/<uuid:shipment_id>/update-tracking/', views.update_tracking, name='update_tracking'),
    path('shipments/<uuid:shipment_id>/generate-label/', views.generate_label, name='generate_label'),
]