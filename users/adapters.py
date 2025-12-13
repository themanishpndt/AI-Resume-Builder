"""
Custom allauth adapter to disable default password reset.
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to use OTP-based password reset instead of allauth's default.
    """
    
    def send_mail(self, template_prefix, email, context):
        """
        Override to prevent allauth from sending password reset emails.
        Our custom OTP system handles password resets.
        """
        # Only block password reset emails, allow other emails
        if template_prefix == 'account/email/password_reset_key':
            # Don't send allauth password reset email
            return
        
        # Allow other emails (verification, etc.)
        super().send_mail(template_prefix, email, context)
    
    def get_login_redirect_url(self, request):
        """
        Redirect to dashboard after login.
        """
        return reverse('dashboard')
    
    def get_signup_redirect_url(self, request):
        """
        Redirect to login page after successful signup with success message.
        """
        messages.success(
            request,
            '🎉 Account created successfully! Please login with your credentials.'
        )
        return reverse('account_login')
    
    def add_message(self, request, level, message_tag, message, extra_tags='', fail_silently=False):
        """
        Override to customize success messages for signup.
        Safely handle message type.
        """
        msg_str = str(message) if not isinstance(message, str) else message
        if 'successfully signed in' in msg_str.lower():
            msg_str = '✅ Welcome! You have successfully logged in.'
        super().add_message(request, level, message_tag, msg_str, extra_tags, fail_silently)
