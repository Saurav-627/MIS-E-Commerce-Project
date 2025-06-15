import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Brand, Product, Review
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
        password='testpass123',
        user_type='customer'
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


@pytest.mark.django_db
class TestProductViews:
    def test_list_products(self, api_client, product):
        url = reverse('products:product-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_get_product_detail(self, api_client, product):
        url = reverse('products:product-detail', kwargs={'slug': product.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name

    def test_create_product_as_seller(self, api_client, seller, category, brand):
        api_client.force_authenticate(user=seller)
        url = reverse('products:product-list')
        data = {
            'category': category.id,
            'brand': brand.id,
            'name': 'New Product',
            'description': 'New product description',
            'price': '149.99',
            'sku': 'NEW-001',
            'stock_quantity': 5,
            'status': 'active'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name='New Product').exists()

    def test_create_product_as_customer_forbidden(self, api_client, user, category, brand):
        api_client.force_authenticate(user=user)
        url = reverse('products:product-list')
        data = {
            'category': category.id,
            'brand': brand.id,
            'name': 'New Product',
            'description': 'New product description',
            'price': '149.99',
            'sku': 'NEW-001',
            'stock_quantity': 5,
            'status': 'active'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_products_by_category(self, api_client, product, category):
        url = reverse('products:product-list')
        response = api_client.get(url, {'category': category.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_search_products(self, api_client, product):
        url = reverse('products:product-list')
        response = api_client.get(url, {'search': 'Test'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_filter_products_by_price_range(self, api_client, product):
        url = reverse('products:product-list')
        response = api_client.get(url, {'min_price': '50', 'max_price': '150'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestProductReviews:
    def test_add_review(self, api_client, user, product):
        api_client.force_authenticate(user=user)
        url = reverse('products:product-add-review', kwargs={'slug': product.slug})
        data = {
            'rating': 5,
            'title': 'Great product!',
            'comment': 'I love this product.'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.filter(product=product, user=user).exists()

    def test_add_duplicate_review_forbidden(self, api_client, user, product):
        # Create first review
        Review.objects.create(
            product=product,
            user=user,
            rating=5,
            title='First review',
            comment='First comment'
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('products:product-add-review', kwargs={'slug': product.slug})
        data = {
            'rating': 4,
            'title': 'Second review',
            'comment': 'Second comment'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_product_reviews(self, api_client, user, product):
        # Create a review
        Review.objects.create(
            product=product,
            user=user,
            rating=5,
            title='Great product!',
            comment='I love this product.'
        )
        
        url = reverse('products:product-reviews', kwargs={'slug': product.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestCategoryViews:
    def test_list_categories(self, api_client, category):
        url = reverse('products:category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_category_detail(self, api_client, category):
        url = reverse('products:category-detail', kwargs={'slug': category.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name


@pytest.mark.django_db
class TestBrandViews:
    def test_list_brands(self, api_client, brand):
        url = reverse('products:brand-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_brand_detail(self, api_client, brand):
        url = reverse('products:brand-detail', kwargs={'slug': brand.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == brand.name