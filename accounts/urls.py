from django.urls import path
from .views_password_reset import (
    PasswordResetCombinedView,
    ResendPasswordResetOTPView,
    ClearPasswordResetJustSentView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
)

urlpatterns = [
    path('password/reset/', PasswordResetCombinedView.as_view(), name='password_reset_request'),
    path('password/reset/verify/', PasswordResetCombinedView.as_view(), name='password_reset_verify_otp'),
    path('password/reset/resend/', ResendPasswordResetOTPView.as_view(), name='resend_password_reset_otp'),
    path('password/reset/clear-just-sent/', ClearPasswordResetJustSentView.as_view(), name='password_reset_clear_just_sent'),
    path('password/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm_simple'),
    path('password/reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password/reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
]
