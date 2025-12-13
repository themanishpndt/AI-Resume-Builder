"""
Diagnostic views to help debug authentication issues on Render.
These should be disabled or protected in production.
"""
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def auth_diagnostic(request):
    """
    Comprehensive authentication diagnostic endpoint.
    
    GET: Show diagnostic form
    POST: Test authentication with provided credentials
    """
    if request.method == "GET":
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Diagnostic</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .section { background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px; }
                .success { color: green; }
                .error { color: red; }
                .warning { color: orange; }
                input, button { padding: 10px; margin: 5px 0; }
                button { background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <h1>🔍 Authentication Diagnostic Tool</h1>
            
            <div class="section">
                <h2>Test Authentication</h2>
                <form method="POST">
                    <input type="email" name="email" placeholder="Email" required style="width: 300px;"><br>
                    <input type="password" name="password" placeholder="Password" required style="width: 300px;"><br>
                    <button type="submit">Test Login</button>
                </form>
            </div>
            
            <div class="section">
                <h2>System Configuration</h2>
                <p><strong>DEBUG:</strong> {debug}</p>
                <p><strong>DATABASE:</strong> {database}</p>
                <p><strong>AUTH_USER_MODEL:</strong> {auth_model}</p>
                <p><strong>AUTHENTICATION_BACKENDS:</strong></p>
                <ul>
                    {backends}
                </ul>
            </div>
            
            <div class="section">
                <h2>Quick Checks</h2>
                <p><a href="/admin/">Admin Panel</a></p>
                <p><a href="/accounts/login/">Login Page</a></p>
                <p><a href="/accounts/signup/">Signup Page</a></p>
            </div>
        </body>
        </html>
        """.format(
            debug=settings.DEBUG,
            database=settings.DATABASES['default']['ENGINE'],
            auth_model=settings.AUTH_USER_MODEL,
            backends=''.join([f'<li>{b}</li>' for b in settings.AUTHENTICATION_BACKENDS])
        )
        return HttpResponse(html)
    
    # POST request - test authentication
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    
    results = {
        'email': email,
        'tests': []
    }
    
    # Test 1: Check if user exists
    try:
        user = CustomUser.objects.get(email=email)
        results['tests'].append({
            'name': 'User Exists',
            'status': 'PASS',
            'message': f'User found: {user.email}',
            'details': {
                'id': user.id,
                'email': user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'date_joined': str(user.date_joined)
            }
        })
        
        # Test 2: Check password
        password_valid = user.check_password(password)
        results['tests'].append({
            'name': 'Password Check',
            'status': 'PASS' if password_valid else 'FAIL',
            'message': 'Password is correct' if password_valid else 'Password is incorrect',
            'details': {
                'password_hash_prefix': user.password[:20] + '...' if user.password else 'No password set'
            }
        })
        
    except CustomUser.DoesNotExist:
        results['tests'].append({
            'name': 'User Exists',
            'status': 'FAIL',
            'message': f'No user found with email: {email}'
        })
    except Exception as e:
        results['tests'].append({
            'name': 'User Lookup',
            'status': 'ERROR',
            'message': str(e)
        })
    
    # Test 3: Test authentication
    try:
        auth_user = authenticate(request, email=email, password=password)
        if auth_user:
            results['tests'].append({
                'name': 'Authentication',
                'status': 'PASS',
                'message': f'Authentication successful for {auth_user.email}'
            })
        else:
            results['tests'].append({
                'name': 'Authentication',
                'status': 'FAIL',
                'message': 'Authentication failed - check password and authentication backends'
            })
    except Exception as e:
        results['tests'].append({
            'name': 'Authentication',
            'status': 'ERROR',
            'message': str(e)
        })
    
    # Test 4: Check authentication backends
    results['tests'].append({
        'name': 'Authentication Backends',
        'status': 'INFO',
        'message': f'{len(settings.AUTHENTICATION_BACKENDS)} backend(s) configured',
        'details': {
            'backends': settings.AUTHENTICATION_BACKENDS
        }
    })
    
    # Generate HTML response
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Test Results</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .section { background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px; }
            .test { padding: 10px; margin: 10px 0; border-left: 4px solid #ccc; }
            .test.pass { border-color: green; background: #e8f5e9; }
            .test.fail { border-color: red; background: #ffebee; }
            .test.error { border-color: orange; background: #fff3e0; }
            .test.info { border-color: blue; background: #e3f2fd; }
            pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🔍 Authentication Test Results</h1>
        <p><a href="/auth-diagnostic/">← Back to Diagnostic Tool</a></p>
        
        <div class="section">
            <h2>Testing Email: {email}</h2>
        </div>
        
        {test_results}
        
        <div class="section">
            <h2>Recommendations</h2>
            {recommendations}
        </div>
        
        <p><a href="/auth-diagnostic/">← Run Another Test</a></p>
    </body>
    </html>
    """
    
    # Generate test results HTML
    test_html = ''
    for test in results['tests']:
        status_class = test['status'].lower()
        details_html = ''
        if 'details' in test:
            import json
            details_html = f'<pre>{json.dumps(test["details"], indent=2)}</pre>'
        
        test_html += f'''
        <div class="test {status_class}">
            <h3>{test["name"]}: {test["status"]}</h3>
            <p>{test["message"]}</p>
            {details_html}
        </div>
        '''
    
    # Generate recommendations
    recommendations = []
    
    # Check test results
    user_exists = any(t['name'] == 'User Exists' and t['status'] == 'PASS' for t in results['tests'])
    password_correct = any(t['name'] == 'Password Check' and t['status'] == 'PASS' for t in results['tests'])
    auth_success = any(t['name'] == 'Authentication' and t['status'] == 'PASS' for t in results['tests'])
    
    if not user_exists:
        recommendations.append('❌ User does not exist. Create user via signup or admin panel.')
    elif not password_correct:
        recommendations.append('❌ Password is incorrect. Reset password or check if password was set correctly.')
    elif not auth_success:
        recommendations.append('⚠️ User exists and password is correct, but authentication failed. Check AUTHENTICATION_BACKENDS configuration.')
    else:
        recommendations.append('✅ All tests passed! User can login successfully.')
    
    recommendations_html = '<ul>' + ''.join([f'<li>{r}</li>' for r in recommendations]) + '</ul>'
    
    return HttpResponse(html.format(
        email=email,
        test_results=test_html,
        recommendations=recommendations_html
    ))


@require_http_methods(["GET"])
def database_diagnostic(request):
    """
    Check database connection and user count.
    """
    try:
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        staff_users = CustomUser.objects.filter(is_staff=True).count()
        
        recent_users = CustomUser.objects.order_by('-date_joined')[:5]
        recent_list = [
            {
                'email': u.email,
                'date_joined': str(u.date_joined),
                'is_active': u.is_active
            }
            for u in recent_users
        ]
        
        return JsonResponse({
            'status': 'success',
            'database': {
                'engine': settings.DATABASES['default']['ENGINE'],
                'name': settings.DATABASES['default'].get('NAME', 'N/A')
            },
            'users': {
                'total': total_users,
                'active': active_users,
                'staff': staff_users,
                'recent': recent_list
            }
        })
    except Exception as e:
        logger.exception("Database diagnostic error")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def email_diagnostic(request):
    """
    Check email configuration.
    """
    config = {
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'Not set'),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'Not set'),
        'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', False),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not set'),
        'EMAIL_HOST_PASSWORD': '***' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'Not set',
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set'),
    }
    
    # Check if SMTP is configured
    is_smtp = 'smtp' in settings.EMAIL_BACKEND.lower()
    has_credentials = bool(getattr(settings, 'EMAIL_HOST_USER', '')) and bool(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
    
    return JsonResponse({
        'status': 'success',
        'configuration': config,
        'analysis': {
            'backend_type': 'SMTP' if is_smtp else 'Console/File',
            'credentials_set': has_credentials,
            'ready_to_send': is_smtp and has_credentials
        }
    })
