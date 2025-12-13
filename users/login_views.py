"""
Custom login view to handle 'Remember me' functionality and prevent 500 errors.
"""
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
import logging
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.utils import ErrorList

logger = logging.getLogger(__name__)


class CustomLoginView(AllauthLoginView):
    """
    Custom login view that extends allauth's LoginView to handle:
    - 'Remember me' checkbox for session persistence
    - Graceful error handling to prevent 500 errors
    - Proper session expiry management
    """
    
    def form_valid(self, form):
        """
        Handle successful form validation.
        Override to add 'Remember me' functionality and welcome message.
        """
        try:
            # Get the 'remember' checkbox value
            remember_me = self.request.POST.get('remember', None)
            
            # Set session expiry based on 'remember me' checkbox
            if remember_me:
                # Remember for 2 weeks (1209600 seconds)
                self.request.session.set_expiry(1209600)
                logger.info("Session set to persist for 2 weeks (Remember me enabled)")
            else:
                # Expire when browser closes (0 = browser-length session)
                self.request.session.set_expiry(0)
                logger.info("Session set to expire on browser close (Remember me disabled)")
            
            # Call parent's form_valid which handles the actual login
            response = super().form_valid(form)
            
            # Add welcome message after successful login
            user = self.request.user
            if user.is_authenticated:
                # Get user's full name or email
                full_name = user.get_full_name() if hasattr(user, 'get_full_name') and user.get_full_name() else user.email
                messages.success(
                    self.request,
                    f'Welcome back, {full_name}! 🎉'
                )
                logger.info(f"✅ User logged in successfully: {user.email}")
            
            return response
            
        except ImmediateHttpResponse:
            # Re-raise allauth's redirect exceptions
            raise
        except Exception as e:
            # Log the error and show user-friendly message
            logger.exception(f"❌ Login error: {str(e)}")
            
            # Check if error message already exists to prevent duplicates
            storage = messages.get_messages(self.request)
            existing_messages = [m.message for m in storage]
            storage.used = False  # Mark messages as not used so they display
            
            error_msg = 'An error occurred during login. Please try again or contact support if the issue persists.'
            if error_msg not in existing_messages:
                messages.error(self.request, error_msg)
                
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """
        Handle form validation errors gracefully.
        """
        try:
            # Log form errors for debugging
            if form.errors:
                logger.warning(f"Login form validation errors: {form.errors}")
                
                # Add a single user-friendly error message if not already present
                # Normalize non-field errors to a single friendly message so the
                # template doesn't show the allauth default and a separate messages
                # framework message (which looked duplicated/confusing).
                friendly = (
                    'Incorrect email or password. Please try again, or use "Forgot password" to reset your password.'
                )

                # Replace any non-field errors with the friendly message
                if form.non_field_errors():
                    form._errors[NON_FIELD_ERRORS] = ErrorList([friendly])

                # Note: we intentionally do NOT duplicate the friendly message in
                # the messages framework here because the template already shows
                # non-field form errors in a dedicated alert block. Keeping the
                # error only in `form.non_field_errors` avoids the same message
                # appearing twice on the page.
            
            return super().form_invalid(form)
            
        except Exception as e:
            # Catch any unexpected errors in form rendering
            logger.exception(f"Error rendering login form: {str(e)}")
            
            # Check if error message already exists
            storage = messages.get_messages(self.request)
            existing_messages = [m.message for m in storage]
            storage.used = False
            
            error_msg = 'An error occurred. Please try again.'
            if error_msg not in existing_messages:
                messages.error(self.request, error_msg)
                
            return render(self.request, self.template_name, {'form': form})
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests gracefully.
        Redirect already authenticated users to dashboard.
        """
        # If user is already authenticated, redirect to dashboard
        if request.user.is_authenticated:
            # Clear any lingering error messages
            storage = messages.get_messages(request)
            storage.used = True  # Mark all messages as used (clear them)
            
            logger.info(f"Already authenticated user {request.user.email} redirected to dashboard")
            return redirect('dashboard')
        
        # Clear any old error messages from previous failed login attempts
        # Only clear if there's no POST data (fresh page load)
        if not request.POST:
            storage = messages.get_messages(request)
            # Check if there are old login error messages
            old_messages = [m for m in storage]
            storage.used = False  # Don't consume yet
            
            # If there are error messages, clear them on fresh GET request
            if old_messages and all(m.level == messages.ERROR for m in old_messages):
                storage.used = True  # Clear old error messages
                logger.info("Cleared old error messages on fresh login page load")
        
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error loading login page: {str(e)}")
            messages.error(
                request,
                'An error occurred loading the login page. Please refresh and try again.'
            )
            # Return a basic login form even if there's an error
            from allauth.account.forms import LoginForm
            form = LoginForm()
            return render(request, self.template_name, {'form': form})
