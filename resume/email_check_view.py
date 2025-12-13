"""
Simple view to check email configuration status (for debugging)
"""
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def check_email_config(request):
    """
    Check if email is properly configured.
    Access at: /check-email-config/
    """
    config = {
        'email_backend': settings.EMAIL_BACKEND,
        'email_host': getattr(settings, 'EMAIL_HOST', 'Not set'),
        'email_port': getattr(settings, 'EMAIL_PORT', 'Not set'),
        'email_use_tls': getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
        'email_host_user_set': bool(settings.EMAIL_HOST_USER),
        'email_host_password_set': bool(settings.EMAIL_HOST_PASSWORD),
        'default_from_email': settings.DEFAULT_FROM_EMAIL,
    }
    
    # Check if properly configured
    is_configured = (
        settings.EMAIL_HOST_USER and 
        settings.EMAIL_HOST_PASSWORD and
        'smtp' in settings.EMAIL_BACKEND.lower()
    )
    
    config['is_properly_configured'] = is_configured
    
    if is_configured:
        config['status'] = '✅ Email is properly configured'
    else:
        config['status'] = '❌ Email is NOT configured - Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD'
        config['missing_variables'] = []
        
        if not settings.EMAIL_HOST_USER:
            config['missing_variables'].append('EMAIL_HOST_USER')
        if not settings.EMAIL_HOST_PASSWORD:
            config['missing_variables'].append('EMAIL_HOST_PASSWORD')
    
    return JsonResponse(config, json_dumps_params={'indent': 2})
