"""
Custom CSRF failure view to handle CSRF errors gracefully.
"""
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def csrf_failure(request, reason=""):
    """
    Custom CSRF failure handler that redirects to login with a friendly message.
    
    This is called when CSRF validation fails, typically when:
    - The CSRF token has expired
    - The user tried to submit a form after their session expired
    - The CSRF token was rotated after a previous login attempt
    """
    logger.warning(f"CSRF failure: {reason} for user {request.user if request.user.is_authenticated else 'anonymous'}")
    
    # Add a user-friendly message
    messages.warning(
        request,
        'Your session has expired. Please try again.'
    )
    
    # Redirect to the login page with a fresh CSRF token
    return redirect('account_login')
