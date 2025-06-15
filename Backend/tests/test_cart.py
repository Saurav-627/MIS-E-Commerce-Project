import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.cart.models import Cart, CartItem, WishlistItem
from apps.products.models import Category, Brand, Product
from decimal import Decimal

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def seller(db):
    return User.objects.create_user(
        username='testseller',
        email='seller@example.com',
        password='testpass123',
        user_type='seller'
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name='Test Category',
        description='Test category description'
    )


@pytest.fixture
def brand(db):
    return Brand.objects.create(
        name='Test Brand',
        description='Test brand description'
    )


@pytest.fixture
def product(db, seller, category, brand):
    return Product.objects.create(
        seller=seller,
        category=category,
        brand=brand,
        name='Test Product',
        description='Test product description',
        price=Decimal('99.99'),
        sku='TEST-001',
        stock_quantity=10,
        status='active'
    )


@pytest.fixture
def cart(db, user):
    return Cart.objects.create(user=user)


@pytest.mark.django_db
class TestCartViews:
    def test_get_cart(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('cart:cart')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.data
        assert response.data['is_empty'] is True

    def test_add_to_cart(self, api_client, user, product):
        api_client.force_authenticate(user=user)
        url = reverse('cart:add_to_cart')
        data = {
            'product_id': str(product.id),
            'quantity': 2
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.filter(cart__user=user, product=product).exists()

    def test_add_to_cart_insufficient_stock(self, api_client, user, product):
        api_client.force_authenticate(user=user)
        url = reverse('cart:add_to_cart')
        data = {
            'product_id': str(product.id),
            'quantity': 20  # More than available stock
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_cart_item(self, api_client, user, product, cart):
        # Create cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('cart:update_cart_item', kwargs={'item_id': cart_item.id})
        data = {'quantity': 3}
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_remove_cart_item(self, api_client, user, product, cart):
        # Create cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('cart:remove_from_cart', kwargs={'item_id': cart_item.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not CartItem.objects.filter(id=cart_item.id).exists()

    def test_clear_cart(self, api_client, user, product, cart):
        # Create cart items
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        api_client.force_authenticate(user=user)
        url = reverse('cart:clear_cart')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not CartItem.objects.filter(cart=cart).exists()


@pytest.mark.django_db
class TestWishlistViews:
    def test_get_wishlist(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('cart:wishlist')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_add_to_wishlist(self, api_client, user, product):
        api_client.force_authenticate(user=user)
        url = reverse('cart:add_to_wishlist')
        data = {'product_id': str(product.id)}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert WishlistItem.objects.filter(user=user, product=product).exists()

    def test_add_duplicate_to_wishlist(self, api_client, user, product):
        # Create wishlist item
        WishlistItem.objects.create(user=user, product=product)
        
        api_client.force_authenticate(user=user)
        url = reverse('cart:add_to_wishlist')
        data = {'product_id': str(product.id)}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_from_wishlist(self, api_client, user, product):
        # Create wishlist item
        wishlist_item = WishlistItem.objects.create(user=user, product=product)
        
        api_client.force_authenticate(user=user)
        url = reverse('cart:remove_from_wishlist', kwargs={'item_id': wishlist_item.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not WishlistItem.objects.filter(id=wishlist_item.id).exists()

    def test_move_to_cart(self, api_client, user, product):
        # Create wishlist item
        wishlist_item = WishlistItem.objects.create(user=user, product=product)
        
        api_client.force_authenticate(user=user)
        url = reverse('cart:move_to_cart', kwargs={'item_id': wishlist_item.id})
        response = api_client.post(url, data={})
        
        assert response.status_code == status.HTTP_200_OK
        assert not WishlistItem.objects.filter(id=wishlist_item.id).exists()
        assert CartItem.objects.filter(cart__user=user, product=product).exists()


@pytest.mark.django_db
class TestCartModels:
    def test_cart_total_items(self, user, product, cart):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        
        assert cart.total_items == 5

    def test_cart_total_price(self, user, product, cart):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        
        expected_total = product.price * 2
        assert cart.total_price == expected_total

    def test_cart_item_total_price(self, user, product, cart):
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=3)
        
        expected_total = product.price * 3
        assert cart_item.total_price == expected_total

    def test_cart_add_item_new(self, user, product, cart):
        cart_item = cart.add_item(product, quantity=2)
        
        assert cart_item.quantity == 2
        assert cart_item.product == product

    def test_cart_add_item_existing(self, user, product, cart):
        # Create existing item
        existing_item = CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        # Add more of the same product
        cart_item = cart.add_item(product, quantity=2)
        
        assert cart_item.id == existing_item.id
        assert cart_item.quantity == 3