"""
Diagnostic view to test login page rendering
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import traceback
import sys


@csrf_exempt
def test_login_diagnostic(request):
    """
    Test if login template can be rendered and handle POST
    """
    if request.method == 'POST':
        try:
            # Get form data
            email = request.POST.get('login', '')
            password = request.POST.get('password', '')
            
            result = {
                'method': 'POST',
                'email_provided': bool(email),
                'password_provided': bool(password),
                'post_data_keys': list(request.POST.keys()),
            }
            
            # Try authentication
            try:
                user = authenticate(request, username=email, password=password)
                result['auth_result'] = 'User found' if user else 'Authentication failed'
                result['user_active'] = user.is_active if user else 'N/A'
            except Exception as auth_error:
                result['auth_error'] = str(auth_error)
                result['auth_traceback'] = traceback.format_exc()
            
            return JsonResponse(result, safe=False, json_dumps_params={'indent': 2})
            
        except Exception as e:
            error_details = traceback.format_exc()
            return JsonResponse({
                'error': str(e),
                'traceback': error_details,
                'python_version': sys.version,
            }, status=500, json_dumps_params={'indent': 2})
    
    # GET request - try to render template
    try:
        from allauth.account.forms import LoginForm
        form = LoginForm()
        context = {
            'form': form,
        }
        return render(request, 'account/login.html', context)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return HttpResponse(f"""
            <h1>Error Details:</h1>
            <pre>{error_details}</pre>
            <hr>
            <h2>Exception: {str(e)}</h2>
            <hr>
            <h3>Python Version: {sys.version}</h3>
        """, content_type="text/html", status=500)


def test_simple(request):
    """Simple test view"""
    import django
    from django.conf import settings
    
    return HttpResponse(f"""
        <h1>✅ Django is working!</h1>
        <p>If you see this, the server is responding.</p>
        <hr>
        <h3>Environment Info:</h3>
        <ul>
            <li>Django Version: {django.get_version()}</li>
            <li>Python Version: {sys.version}</li>
            <li>DEBUG: {settings.DEBUG}</li>
            <li>ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}</li>
            <li>DATABASE: {settings.DATABASES['default']['ENGINE']}</li>
        </ul>
        <hr>
        <h3>Test Links:</h3>
        <ul>
            <li><a href="/test-login/">Test Login Diagnostic</a></li>
            <li><a href="/accounts/login/">Actual Login Page</a></li>
            <li><a href="/accounts/signup/">Actual Signup Page</a></li>
        </ul>
    """)

