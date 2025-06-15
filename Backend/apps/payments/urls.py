from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'payment-methods', views.PaymentMethodViewSet, basename='payment-method')

urlpatterns = [
    path('', include(router.urls)),
    path('process/', views.process_payment, name='process_payment'),
    path('refund/', views.create_refund, name='create_refund'),
    
    # Webhook endpoints
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/paypal/', views.paypal_webhook, name='paypal_webhook'),
]