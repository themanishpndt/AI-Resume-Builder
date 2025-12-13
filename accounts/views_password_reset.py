"""
Lightweight wrapper views for password reset that reuse existing resume.password_reset_views
This file provides an explicit module as requested while delegating logic to the existing implementation.
"""
from resume import password_reset_views as resume_views

# Re-expose the key classes/objects here so other code can import from accounts.views_password_reset
PasswordResetRequestView = resume_views.PasswordResetRequestView
PasswordResetVerifyOTPView = resume_views.PasswordResetVerifyOTPView
PasswordResetCombinedView = resume_views.PasswordResetCombinedView
PasswordResetConfirmView = resume_views.PasswordResetConfirmView
PasswordResetCompleteView = resume_views.PasswordResetCompleteView
ResendPasswordResetOTPView = resume_views.ResendPasswordResetOTPView
PasswordResetDoneView = resume_views.PasswordResetDoneView
ClearPasswordResetJustSentView = resume_views.ClearPasswordResetJustSentView

__all__ = [
    'PasswordResetRequestView', 'PasswordResetVerifyOTPView', 'PasswordResetCombinedView',
    'PasswordResetConfirmView', 'PasswordResetCompleteView', 'ResendPasswordResetOTPView',
    'PasswordResetDoneView', 'ClearPasswordResetJustSentView'
]
