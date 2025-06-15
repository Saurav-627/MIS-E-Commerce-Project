from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'coupons', views.CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', views.create_order, name='create_order'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
]