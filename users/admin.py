from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, SignupOTP, PasswordResetOTP


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Enhanced admin interface for CustomUser model with full database access.
    """
    list_display = [
        'email', 
        'get_full_name', 
        'username',
        'phone',
        'is_staff_badge',
        'is_active_badge',
        'created_at'
    ]
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'username', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'profile_photo', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'first_name', 'last_name', 'phone')}),
    )
    
    def is_staff_badge(self, obj):
        """Display staff status as colored badge."""
        if obj.is_staff:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Staff</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">User</span>'
        )
    is_staff_badge.short_description = 'Staff Status'
    
    def is_active_badge(self, obj):
        """Display active status as colored badge."""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(SignupOTP)
class SignupOTPAdmin(admin.ModelAdmin):
    """Admin interface for Signup OTP."""
    list_display = ['email', 'first_name', 'last_name', 'otp', 'created_at', 'is_verified', 'is_valid_badge']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'otp']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def is_valid_badge(self, obj):
        """Display OTP validity status as colored badge."""
        if obj.is_valid():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Valid</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Expired/Verified</span>'
        )
    is_valid_badge.short_description = 'Validity'


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    """Admin interface for Password Reset OTP."""
    list_display = ['user', 'otp', 'created_at', 'is_used', 'is_valid_badge']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'otp']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def is_valid_badge(self, obj):
        """Display OTP validity status as colored badge."""
        if obj.is_valid():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Valid</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Expired/Used</span>'
        )
    is_valid_badge.short_description = 'Validity'
