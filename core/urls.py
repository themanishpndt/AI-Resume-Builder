"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from resume.password_reset_views import (
    PasswordResetRequestView,
    PasswordResetVerifyOTPView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from resume.password_reset_views import ResendPasswordResetOTPView, PasswordResetCombinedView, ClearPasswordResetJustSentView
from resume.password_reset_views import PasswordResetDoneView
from resume.email_check_view import check_email_config
from resume.test_login_view import test_login_diagnostic, test_simple
from users.login_views import CustomLoginView
from users.signup_views import CustomSignupView
from users.signup_otp_views import SignupRequestView, SignupVerifyOTPView, ResendSignupOTPView
from users.logout_views import CustomLogoutView, QuickLogoutView
from users.diagnostic_views import auth_diagnostic, database_diagnostic, email_diagnostic
from users.delete_account_views import delete_account, DeleteAccountView

# Custom error handlers
handler400 = 'core.error_handlers.handler400'
handler403 = 'core.error_handlers.handler403'
handler404 = 'core.error_handlers.handler404'
handler500 = 'core.error_handlers.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Diagnostic endpoints
    path('check-email-config/', check_email_config, name='check_email_config'),
    path('test-login/', test_login_diagnostic, name='test_login_diagnostic'),
    path('test-simple/', test_simple, name='test_simple'),
    path('auth-diagnostic/', auth_diagnostic, name='auth_diagnostic'),
    path('database-diagnostic/', database_diagnostic, name='database_diagnostic'),
    path('email-diagnostic/', email_diagnostic, name='email_diagnostic'),
    
    # Custom authentication views (must be before allauth)
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', SignupRequestView.as_view(), name='account_signup'),
    path('accounts/signup/verify-otp/', SignupVerifyOTPView.as_view(), name='signup_verify_otp'),
    path('accounts/signup/resend-otp/', ResendSignupOTPView.as_view(), name='resend_signup_otp'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='account_logout'),
    path('accounts/quick-logout/', QuickLogoutView.as_view(), name='quick_logout'),
    
    # Account management
    path('accounts/delete/', delete_account, name='delete_account'),
    path('accounts/delete/confirm/', DeleteAccountView.as_view(), name='delete_account_confirm'),
    
    # Delegate password-reset related routes to the accounts app (keeps routing centralized)
    path('accounts/', include('accounts.urls')),
    
    # Allauth URLs (our custom views will override)
    path('accounts/', include('allauth.urls')),
    
    # Resume app URLs
    path('', include('resume.urls')),
]

# Serve media files in both development and production
# For production: Consider using cloud storage (AWS S3, Cloudinary, etc.) for persistent storage
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files only in development (WhiteNoise handles in production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
