"""
Global error handlers to prevent 502 errors by catching all exceptions.
These handlers ensure the application never crashes the Gunicorn worker.
"""
from django.shortcuts import render
from django.http import JsonResponse
import logging
import traceback

logger = logging.getLogger(__name__)


def handler500(request, *args, **kwargs):
    """
    Custom 500 error handler to prevent worker crashes.
    Logs the full error and returns a user-friendly page.
    """
    try:
        # Log the full traceback
        logger.error("=" * 80)
        logger.error("500 INTERNAL SERVER ERROR")
        logger.error("=" * 80)
        logger.error(f"Path: {request.path}")
        logger.error(f"Method: {request.method}")
        logger.error(f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}")
        
        # Log POST data (excluding sensitive fields)
        if request.method == 'POST':
            safe_post = {k: v for k, v in request.POST.items() if k not in ['password', 'password1', 'password2']}
            logger.error(f"POST data: {safe_post}")
        
        # Log the exception if available
        if hasattr(kwargs, 'exception'):
            logger.error(f"Exception: {kwargs['exception']}")
            logger.error(traceback.format_exc())
        
        logger.error("=" * 80)
        
    except Exception as e:
        # Even error logging shouldn't crash
        logger.error(f"Error in error handler: {str(e)}")
    
    # Return user-friendly error page
    context = {
        'error_code': 500,
        'error_title': 'Internal Server Error',
        'error_message': 'Something went wrong on our end. Our team has been notified.',
        'show_home_link': True,
        'show_support_link': True,
    }
    
    return render(request, 'errors/500.html', context, status=500)


def handler404(request, exception):
    """
    Custom 404 error handler.
    """
    logger.warning(f"404 Not Found: {request.path}")
    
    context = {
        'error_code': 404,
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.',
        'show_home_link': True,
    }
    
    return render(request, 'errors/404.html', context, status=404)


def handler403(request, exception):
    """
    Custom 403 error handler.
    """
    logger.warning(f"403 Forbidden: {request.path} by {request.user}")
    
    context = {
        'error_code': 403,
        'error_title': 'Access Denied',
        'error_message': 'You do not have permission to access this page.',
        'show_home_link': True,
    }
    
    return render(request, 'errors/403.html', context, status=403)


def handler400(request, exception):
    """
    Custom 400 error handler.
    """
    logger.warning(f"400 Bad Request: {request.path}")
    
    context = {
        'error_code': 400,
        'error_title': 'Bad Request',
        'error_message': 'Your request could not be processed. Please check your input.',
        'show_home_link': True,
    }
    
    return render(request, 'errors/400.html', context, status=400)
