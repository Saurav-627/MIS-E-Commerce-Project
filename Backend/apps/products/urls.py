from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'products'

# Main router
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'reviews', views.ReviewViewSet, basename='review')

# Nested router for product images
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'images', views.ProductImageViewSet, basename='product-images')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
]