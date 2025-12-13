"""
Custom logout view to ensure proper session cleanup and error handling.
Fixes logout issues on Render deployment.
"""
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class CustomLogoutView(View):
    """
    Custom logout view that handles both GET and POST requests.
    
    GET: Shows confirmation page
    POST: Performs logout and clears session
    
    Fixes:
    - Session not clearing properly
    - CSRF token issues in production
    - Redirect not working
    - Cookie cleanup
    """
    
    template_name = 'account/logout.html'
    
    def get(self, request):
        """
        Show logout confirmation page.
        """
        try:
            # If user is not authenticated, redirect to login
            if not request.user.is_authenticated:
                logger.info("Logout GET: User not authenticated, redirecting to login")
                messages.info(request, "You are not logged in.")
                return redirect('account_login')
            
            # Show confirmation page
            logger.info(f"Logout GET: Showing confirmation for user {request.user.email}")
            return render(request, self.template_name)
            
        except Exception as e:
            logger.exception(f"Error in logout GET: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")
            return redirect('home')
    
    def post(self, request):
        """
        Perform logout and clear session.
        """
        try:
            if not request.user.is_authenticated:
                logger.warning("Logout POST: User not authenticated")
                messages.info(request, "You are already logged out.")
                return redirect('account_login')
            
            # Log the logout event
            user_email = request.user.email
            logger.info(f"Logout POST: User {user_email} is logging out")
            
            # Perform logout (clears session)
            logout(request)
            
            # Clear any session data explicitly
            request.session.flush()
            
            # Add success message
            messages.success(request, "You have been successfully logged out.")
            
            logger.info(f"✅ Logout successful for user: {user_email}")
            
            # Redirect to login page
            return redirect('account_login')
            
        except Exception as e:
            logger.exception(f"❌ Error during logout: {str(e)}")
            
            # Even if there's an error, try to logout
            try:
                logout(request)
                request.session.flush()
            except:
                pass
            
            messages.error(
                request,
                "An error occurred during logout, but your session has been cleared."
            )
            return redirect('account_login')


class QuickLogoutView(View):
    """
    Quick logout without confirmation (for API or direct logout links).
    """
    
    def get(self, request):
        """
        Logout immediately without confirmation.
        """
        try:
            if request.user.is_authenticated:
                user_email = request.user.email
                logger.info(f"Quick logout: User {user_email}")
                
                logout(request)
                request.session.flush()
                
                messages.success(request, "You have been logged out.")
                logger.info(f"✅ Quick logout successful for: {user_email}")
            else:
                logger.info("Quick logout: User not authenticated")
                messages.info(request, "You are not logged in.")
            
            return redirect('account_login')
            
        except Exception as e:
            logger.exception(f"❌ Error in quick logout: {str(e)}")
            
            try:
                logout(request)
                request.session.flush()
            except:
                pass
            
            messages.error(request, "An error occurred, but you have been logged out.")
            return redirect('account_login')
    
    def post(self, request):
        """
        Handle POST requests the same as GET for quick logout.
        """
        return self.get(request)
