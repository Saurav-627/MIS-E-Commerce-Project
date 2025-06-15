from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/detail/', views.UserProfileDetailView.as_view(), name='profile_detail'),
    
    # Addresses
    path('addresses/', views.AddressListCreateView.as_view(), name='address_list'),
    path('addresses/<uuid:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    
    # Password Management
    path('change-password/', views.change_password, name='change_password'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
]