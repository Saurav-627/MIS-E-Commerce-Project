import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import UserProfile, Address

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpass123',
        'password_confirm': 'testpass123'
    }


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.mark.django_db
class TestUserRegistration:
    def test_user_registration_success(self, api_client, user_data):
        url = reverse('users:register')
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert User.objects.filter(email=user_data['email']).exists()
        
        # Check if user profile was created
        user = User.objects.get(email=user_data['email'])
        assert hasattr(user, 'profile')

    def test_user_registration_password_mismatch(self, api_client, user_data):
        user_data['password_confirm'] = 'differentpass'
        url = reverse('users:register')
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(email=user_data['email']).exists()

    def test_user_registration_duplicate_email(self, api_client, user_data, user):
        url = reverse('users:register')
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    def test_user_login_success(self, api_client, user):
        url = reverse('users:login')
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data

    def test_user_login_invalid_credentials(self, api_client, user):
        url = reverse('users:login')
        data = {
            'email': user.email,
            'password': 'wrongpass'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfile:
    def test_get_user_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('users:profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_update_user_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('users:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'


@pytest.mark.django_db
class TestUserAddresses:
    @pytest.fixture
    def address_data(self):
        return {
            'address_type': 'shipping',
            'first_name': 'Test',
            'last_name': 'User',
            'address_line_1': '123 Test St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'US',
            'is_default': True
        }

    def test_create_address(self, api_client, user, address_data):
        api_client.force_authenticate(user=user)
        url = reverse('users:address_list')
        response = api_client.post(url, address_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Address.objects.filter(user=user).exists()

    def test_list_addresses(self, api_client, user, address_data):
        api_client.force_authenticate(user=user)
        
        # Create an address
        Address.objects.create(user=user, **address_data)
        
        url = reverse('users:address_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_default_address_uniqueness(self, api_client, user, address_data):
        api_client.force_authenticate(user=user)
        
        # Create first default address
        url = reverse('users:address_list')
        response = api_client.post(url, address_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Create second default address
        address_data['address_line_1'] = '456 Another St'
        response = api_client.post(url, address_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that only one default address exists
        default_addresses = Address.objects.filter(
            user=user,
            address_type='shipping',
            is_default=True
        )
        assert default_addresses.count() == 1