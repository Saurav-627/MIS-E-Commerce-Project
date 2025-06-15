from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart endpoints
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('items/<uuid:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('items/<uuid:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    
    # Wishlist endpoints
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/items/<uuid:item_id>/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/items/<uuid:item_id>/move-to-cart/', views.move_to_cart, name='move_to_cart'),
]