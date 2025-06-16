from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ['address_type', 'first_name', 'last_name', 'city', 'state', 'country', 'is_default']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    list_display = ['email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth', 'user_type', 'is_verified', 'avatar')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'user_type')
        }),
    )
    
    # Add AddressInline here for UserAdmin
    inlines = [AddressInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin
    """
    list_display = ['user', 'company', 'location', 'newsletter_subscription', 'created_at']
    list_filter = ['newsletter_subscription', 'email_notifications', 'sms_notifications', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    # AddressInline should not be here
    # Remove inlines from UserProfileAdmin as it's now in UserAdmin


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Address admin
    """
    list_display = ['user', 'address_type', 'first_name', 'last_name', 'city', 'state', 'country', 'is_default']
    list_filter = ['address_type', 'country', 'state', 'is_default', 'created_at']
    search_fields = ['user__email', 'first_name', 'last_name', 'city', 'state', 'country']
    readonly_fields = ['created_at', 'updated_at']
