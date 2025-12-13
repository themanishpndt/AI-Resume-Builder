"""
Custom signup view to ensure proper database saving and error handling.
"""
from allauth.account.views import SignupView as AllauthSignupView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction
import logging

logger = logging.getLogger(__name__)


class CustomSignupView(AllauthSignupView):
    """
    Custom signup view that extends allauth's SignupView to:
    - Ensure users are saved to the database properly
    - Handle database errors gracefully
    - Provide better error messages
    """
    
    def form_valid(self, form):
        """
        Handle successful form validation and user creation.
        """
        try:
            # Use atomic transaction to ensure data integrity
            with transaction.atomic():
                # Create the user using the form save (this respects allauth hooks)
                user = form.save(self.request)

                # Log successful signup
                logger.info(f"User successfully created: {user.email} (ID: {user.pk})")

                # If email verification is enabled, allauth will handle sending it.
                # We redirect users to the login page with a success message so they can confirm their email.
                messages.success(
                    self.request,
                    'Account created successfully. Please check your email for verification (if enabled) and log in.'
                )

                return redirect('account_login')

        except IntegrityError as e:
            # Handle duplicate email or username
            logger.warning(f"Signup IntegrityError: {str(e)}")
            
            if 'email' in str(e).lower():
                form.add_error('email', 'A user with this email already exists. Try logging in instead.')
            elif 'username' in str(e).lower():
                form.add_error('username', 'This username is already taken.')
            else:
                form.add_error(None, 'An account with these details already exists.')
            
            return self.form_invalid(form)
            
        except Exception as e:
            # Handle any other unexpected errors
            logger.exception(f"Unexpected error during signup: {str(e)}")
            messages.error(
                self.request,
                'An error occurred while creating your account. Please try again or contact support.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """
        Handle form validation errors gracefully.
        """
        try:
            # Log form errors for debugging
            if form.errors:
                logger.warning(f"Signup form validation errors: {form.errors}")
            
            return super().form_invalid(form)
            
        except Exception as e:
            # Catch any unexpected errors in form rendering
            logger.exception(f"Error rendering signup form: {str(e)}")
            messages.error(
                self.request,
                'An error occurred. Please try again.'
            )
            return render(self.request, self.template_name, {'form': form})
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests gracefully.
        """
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error loading signup page: {str(e)}")
            messages.error(
                request,
                'An error occurred loading the signup page. Please refresh and try again.'
            )
            # Return a basic signup form even if there's an error
            from allauth.account.forms import SignupForm
            from users.forms import CustomSignupForm
            form = CustomSignupForm()
            return render(request, self.template_name, {'form': form})
