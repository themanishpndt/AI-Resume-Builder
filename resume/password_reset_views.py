"""
Custom password reset views using OTP instead of token links.
"""
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser, PasswordResetOTP
from django import forms
from django.utils.translation import gettext_lazy as _
import logging
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

logger = logging.getLogger(__name__)
# Cooldown in seconds between OTP sends (short for testing)
COOLDOWN_SECONDS = 10


class PasswordResetRequestForm(forms.Form):
    """Form to request password reset via email."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )


class OTPVerificationForm(forms.Form):
    """Form to verify OTP."""
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6'
        })
    )


class NewPasswordForm(forms.Form):
    """Form to set new password."""
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(max_length=6, widget=forms.HiddenInput())
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        # Attach errors to specific fields (so the template displays them inline like signup)
        if password1 and password2 and password1 != password2:
            self.add_error('password2', _('Passwords do not match. Please re-enter your new password.'))

        # Enforce stronger password rules: min 8 chars, uppercase, lowercase, number
        if password1:
            errors = []
            if len(password1) < 8:
                errors.append(_('be at least 8 characters'))
            if not any(c.isupper() for c in password1):
                errors.append(_('include an uppercase letter'))
            if not any(c.islower() for c in password1):
                errors.append(_('include a lowercase letter'))
            if not any(c.isdigit() for c in password1):
                errors.append(_('include a number'))
            if errors:
                # Add a helpful error message to password1 field so it shows beside the input
                self.add_error('password1', _('Password must ') + ', '.join(errors) + '.')

        return cleaned_data


class PasswordResetRequestView(View):
    """Step 1: User enters email to receive OTP."""
    # Use the main password_reset.html as the canonical combined template
    template_name = 'account/password_reset.html'
    
    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        form = PasswordResetRequestForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        form = PasswordResetRequestForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
                
                # Rate limiting: Check if user requested OTP recently (within last 1 minute)
                recent_otp = PasswordResetOTP.objects.filter(
                    user=user,
                    created_at__gte=timezone.now() - timedelta(seconds=COOLDOWN_SECONDS)
                ).first()
                
                if recent_otp:
                    messages.warning(
                        request,
                        f'An OTP was recently sent to your email. Please wait {COOLDOWN_SECONDS} seconds before requesting another one.'
                    )
                    logger.warning(f"Rate limit hit for password reset: {email}")
                    return render(request, self.template_name, {'form': form})
                
                # Generate OTP
                otp_code = PasswordResetOTP.generate_otp()
                
                # Delete old unused OTPs for this user (keep only the newest)
                PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
                
                # Create new OTP
                PasswordResetOTP.objects.create(user=user, otp=otp_code)
                logger.info(f"OTP generated for user: {email}")
                
                # Send OTP via email
                subject = 'Secure Password Reset — AI Resume Builder'
                message = f'''Hello {user.get_full_name()},

Secure Password Reset — Email Verification

You have requested to reset your password for your AI Resume Builder account.

Your 6-digit OTP code is: {otp_code}

This OTP is valid for 10 minutes.

How it works:
- We generated a one-time, 6-digit code and sent it to your email.
- Enter the code on the verification page to confirm your identity and proceed to set a new secure password.

Security tip:
Keep your account safe by choosing a long, unique password and never sharing this code with anyone.

If you did not request this password reset, please ignore this email and your password will remain unchanged.

Best regards,
AI Resume Builder Team
'''
                
                try:
                    # Attempt to send email
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    logger.info(f"✅ OTP email sent successfully to {email}")
                    # Store email and sent time in session for frontend banner and cooldown
                    request.session['password_reset_email'] = email
                    request.session['password_reset_sent_at'] = timezone.now().isoformat()
                    # Mark that an OTP was just sent so the banner appears only immediately after sending
                    request.session['password_reset_just_sent'] = True
                    # For local development: expose the OTP in session so developers can test flows
                    if getattr(settings, 'DEBUG', False):
                        request.session['password_reset_debug_otp'] = otp_code
                    # Store email in session so verify page and resend can use it
                    request.session['password_reset_email'] = email
                    request.session['password_reset_sent_at'] = timezone.now().isoformat()
                    request.session['password_reset_just_sent'] = True
                    messages.success(request, 'An OTP has been sent to your registered email address. Please check your inbox.')
                    return redirect('password_reset_verify_otp')
                    
                except Exception as e:
                    # Log the error with full details
                    logger.error(f"❌ Failed to send OTP email to {email}")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.error(f"Error message: {str(e)}")
                    logger.error(f"Email Backend: {settings.EMAIL_BACKEND}")
                    logger.error(f"Email Host: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
                    logger.error(f"Email Port: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
                    logger.error(f"Email Host User: {settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else 'NOT SET'}")
                    logger.error(f"Email Use TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
                    
                    # Provide detailed error message for debugging
                    # On any email send failure, show a simple red error message per spec
                    logger.exception(f"Email send failure details: {e}")
                    messages.error(request, 'Unable to send OTP. Please check your internet or try again later.')
                    return render(request, self.template_name, {'form': form})
                
            except CustomUser.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
                return render(request, self.template_name, {'form': form})
            except Exception as e:
                # Catch any other unexpected errors
                logger.exception(f"❌ Unexpected error in password reset: {str(e)}")
                messages.error(request, 'An unexpected error occurred. Please try again.')
                return render(request, self.template_name, {'form': form})
        
        return render(request, self.template_name, {'form': form})


class PasswordResetVerifyOTPView(View):
    """Step 2: User enters OTP to verify."""
    template_name = 'account/password_reset.html'
    
    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        # If an email was recently used to request OTP, pre-fill it
        initial = {}
        if request.session.get('password_reset_email'):
            initial['email'] = request.session.get('password_reset_email')
        form = OTPVerificationForm(initial=initial)
        return render(request, self.template_name, {'form': form})


class PasswordResetCombinedView(View):
    """Combined page that allows requesting an OTP and verifying it on the same page.

    The template expects two possible actions from the POST:
      - send_otp (submit button name) to request a new OTP
      - verify_otp to verify an entered OTP
    """
    template_name = 'account/password_reset_verify_otp.html'

    def get(self, request, *args, **kwargs):
        # Prepare both forms: request form and otp verification form
        request_form = PasswordResetRequestForm()
        initial = {}
        if request.session.get('password_reset_email'):
            initial['email'] = request.session.get('password_reset_email')
        otp_form = OTPVerificationForm(initial=initial)
        # Compute server-side cooldown remaining (so timer persists across reloads)
        resend_remaining = 0
        sent_at = request.session.get('password_reset_sent_at')
        if sent_at:
            try:
                from datetime import datetime as _dt
                sent_dt = _dt.fromisoformat(sent_at)
                elapsed = (timezone.now() - sent_dt).total_seconds()
                resend_remaining = max(0, COOLDOWN_SECONDS - int(elapsed))
            except Exception:
                resend_remaining = 0

        return render(request, self.template_name, {
            'request_form': request_form,
            'form': otp_form,
            'resend_cooldown_remaining': resend_remaining,
        })

    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        # Distinguish action by submit button name
        if 'send_otp' in request.POST:
            # Process send OTP (same as PasswordResetRequestView.post)
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                    user = CustomUser.objects.get(email=email, is_active=True)
                    recent_otp = PasswordResetOTP.objects.filter(
                        user=user,
                        created_at__gte=timezone.now() - timedelta(seconds=COOLDOWN_SECONDS)
                    ).first()
                    if recent_otp:
                        messages.warning(request, f'An OTP was recently sent. Please wait {COOLDOWN_SECONDS} seconds before requesting another one.')
                        return redirect('password_reset_verify_otp')

                    otp_code = PasswordResetOTP.generate_otp()
                    PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
                    PasswordResetOTP.objects.create(user=user, otp=otp_code)

                    subject = 'Secure Password Reset — AI Resume Builder'
                    message = f"""Hello {user.get_full_name()},\n\nYour 6-digit OTP code is: {otp_code}\n\nThis OTP is valid for 10 minutes."""
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                    # Store email and sent time in session for frontend banner and cooldown
                    request.session['password_reset_email'] = email
                    request.session['password_reset_sent_at'] = timezone.now().isoformat()
                    # Mark that an OTP was just sent so the banner appears only immediately after sending
                    request.session['password_reset_just_sent'] = True
                    # For local development: expose the OTP in session so developers can test flows
                    if getattr(settings, 'DEBUG', False):
                        request.session['password_reset_debug_otp'] = otp_code
                    messages.success(request, 'An OTP has been sent to your registered email address. Please check your inbox.')
                    return redirect('password_reset_verify_otp')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'No account found with this email address.')
                except Exception as e:
                    logger.exception(f"❌ Error sending OTP in combined view: {str(e)}")
                    messages.error(request, 'Unable to send OTP. Please check your internet or try again later.')

            # If form invalid, render page with errors
            otp_form = OTPVerificationForm()
            return render(request, self.template_name, {'request_form': form, 'form': otp_form})

        elif 'verify_otp' in request.POST:
            # Process OTP verification (same as PasswordResetVerifyOTPView.post)
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                otp = form.cleaned_data['otp']
                try:
                    user = CustomUser.objects.get(email=email, is_active=True)
                    session_key = f'otp_attempts_{email}'
                    attempts = request.session.get(session_key, 0)
                    if attempts >= 5:
                        messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                        request.session[session_key] = 0
                        return redirect('password_reset_request')

                    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).order_by('-created_at').first()
                    if otp_obj and otp_obj.is_valid():
                        # Instead of redirecting, render the same page and show the new password form inline
                        request.session['reset_email'] = email
                        request.session['reset_otp'] = otp
                        request.session[session_key] = 0
                        messages.success(request, 'OTP verified successfully! Please set your new password.')
                        # Prepare forms for rendering: keep request/otp forms and show password form
                        request_form = PasswordResetRequestForm()
                        otp_form = OTPVerificationForm(initial={'email': email})
                        new_password_form = NewPasswordForm(initial={'email': email, 'otp': otp})
                        return render(request, self.template_name, {
                            'request_form': request_form,
                            'form': otp_form,
                            'show_new_password': True,
                            'new_password_form': new_password_form,
                            'resend_cooldown_remaining': 0,
                        })
                    else:
                        request.session[session_key] = attempts + 1
                        remaining = 5 - (attempts + 1)
                        if remaining > 0:
                            messages.error(request, f'Invalid or expired OTP. You have {remaining} attempt(s) remaining.')
                        else:
                            messages.error(request, 'Invalid or expired OTP. Please request a new one.')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Invalid email address.')
            # Render page with errors
            request_form = PasswordResetRequestForm()
            return render(request, self.template_name, {'request_form': request_form, 'form': form})

        elif 'set_new_password' in request.POST:
            # Handle inline new password submission from the combined page
            form = NewPasswordForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                otp = form.cleaned_data.get('otp')
                password = form.cleaned_data.get('password1')
                try:
                    user = CustomUser.objects.get(email=email, is_active=True)

                    otp_obj = PasswordResetOTP.objects.filter(
                        user=user,
                        otp=otp,
                        is_used=False
                    ).order_by('-created_at').first()

                    if otp_obj and otp_obj.is_valid():
                        user.set_password(password)
                        user.save()

                        otp_obj.is_used = True
                        otp_obj.save()

                        # Clear session reset flags
                        request.session.pop('reset_email', None)
                        request.session.pop('reset_otp', None)
                        request.session.pop('password_reset_email', None)
                        request.session.pop('password_reset_just_sent', None)

                        messages.success(request, 'Password reset successful. You can now sign in with your new password.')
                        return redirect('password_reset_done')
                    else:
                        messages.error(request, 'Invalid OTP. Please try again.')
                        return redirect('password_reset_verify_otp')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Invalid user.')
                    return redirect('password_reset_request')
            else:
                # Show form with errors inline
                request_form = PasswordResetRequestForm()
                otp_form = OTPVerificationForm(initial={'email': request.POST.get('email', '')})
                return render(request, self.template_name, {'request_form': request_form, 'form': otp_form, 'show_new_password': True, 'new_password_form': form})

        # Unknown action: reload page
        return redirect('password_reset_verify_otp')


class PasswordResetConfirmView(View):
    """Step 3: User sets new password after OTP verification."""
    template_name = 'account/password_reset_confirm.html'
    
    def get(self, request, *args, **kwargs):
        # Support two flows:
        # 1) OTP-based flow: requires 'reset_email' and 'reset_otp' in session
        # 2) Token-based flow: URL may provide uidb64 and token (compatibility)
        uidb64 = request.resolver_match.kwargs.get('uidb64') if request.resolver_match else None
        token = request.resolver_match.kwargs.get('token') if request.resolver_match else None

        if uidb64 and token:
            # Try to validate token and prepare session for password reset
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = CustomUser.objects.get(pk=uid, is_active=True)
                if default_token_generator.check_token(user, token):
                    # Place identifying data in session so the same form can be used
                    request.session['reset_email'] = user.email
                    request.session['reset_token'] = token
                else:
                    messages.error(request, 'Invalid or expired reset link.')
                    return redirect('password_reset_request')
            except Exception:
                messages.error(request, 'Invalid reset link.')
                return redirect('password_reset_request')

        if 'reset_email' not in request.session:
            messages.error(request, 'Please verify OTP first.')
            return redirect('password_reset_verify_otp')

        form_initial = {'email': request.session.get('reset_email'), 'otp': request.session.get('reset_otp', '')}
        form = NewPasswordForm(initial=form_initial)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = NewPasswordForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = form.cleaned_data['otp']
            password = form.cleaned_data['password1']
            
            try:
                user = CustomUser.objects.get(email=email, is_active=True)

                # If a token-based flow is in progress, validate token and reset password
                token_in_session = request.session.get('reset_token')
                if token_in_session:
                    if default_token_generator.check_token(user, token_in_session):
                        user.set_password(password)
                        user.save()
                        # Clear token/session keys
                        request.session.pop('reset_email', None)
                        request.session.pop('reset_token', None)
                        messages.success(request, 'Your password has been reset successfully!')
                        return redirect('password_reset_done')
                    else:
                        messages.error(request, 'Invalid or expired reset token.')
                        return redirect('password_reset_request')

                # Otherwise expect OTP-based flow
                otp_obj = PasswordResetOTP.objects.filter(
                    user=user,
                    otp=otp,
                    is_used=False
                ).order_by('-created_at').first()

                if otp_obj and otp_obj.is_valid():
                    # Set new password
                    user.set_password(password)
                    user.save()

                    # Mark OTP as used
                    otp_obj.is_used = True
                    otp_obj.save()

                    # Clear session
                    request.session.pop('reset_email', None)
                    request.session.pop('reset_otp', None)

                    messages.success(request, 'Your password has been reset successfully!')
                    return redirect('password_reset_done')
                else:
                    messages.error(request, 'Invalid or expired OTP.')
                    return redirect('password_reset_request')
                    
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid user.')
                return redirect('password_reset_request')
        
        return render(request, self.template_name, {'form': form})


class PasswordResetCompleteView(View):
    """Step 4: Show success message."""
    template_name = 'account/password_reset_complete.html'
    
    def get(self, request):
        return render(request, self.template_name)


class PasswordResetDoneView(View):
    """Simple success page shown after a successful password reset.

    This is the friendly confirmation page the frontend redirects to after
    a successful password change. It intentionally keeps a compact template
    to meet the requirement of a clear success page.
    """
    template_name = 'account/password_reset_done.html'

    def get(self, request):
        return render(request, self.template_name)


class ResendPasswordResetOTPView(View):
    """Resend OTP for password reset verification.

    Reads email from session (set when requesting OTP) and sends a new OTP.
    Applies same basic checks as PasswordResetRequestView (rate-limiting and replacement of old OTP).
    """

    def get(self, request):
        # Allow GET requests to redirect to the verify page (useful for link clicks)
        email = request.session.get('password_reset_email')
        if not email:
            messages.error(request, 'No password reset session found. Please request a reset first.')
            return redirect('password_reset_request')
        messages.info(request, 'Preparing to resend OTP to the email on file. Click Send new OTP to confirm.')
        return redirect('password_reset_verify_otp')

    def post(self, request):
        email = request.session.get('password_reset_email')

        if not email:
            messages.error(request, 'No password reset session found. Please request a reset first.')
            return redirect('password_reset_request')

        try:
            user = CustomUser.objects.get(email=email, is_active=True)

            # Rate limiting: avoid frequent resend (1 minute)
            recent_otp = PasswordResetOTP.objects.filter(
                user=user,
                created_at__gte=timezone.now() - timedelta(seconds=COOLDOWN_SECONDS)
            ).first()

            if recent_otp:
                messages.warning(
                    request,
                    f'An OTP was recently sent. Please wait {COOLDOWN_SECONDS} seconds before requesting another one.'
                )
                return redirect('password_reset_verify_otp')

            # Generate new OTP
            new_otp = PasswordResetOTP.generate_otp()

            # Delete old unused OTPs and create a new one
            PasswordResetOTP.objects.filter(user=user, is_used=False).delete()
            PasswordResetOTP.objects.create(user=user, otp=new_otp)

            # Send email
            subject = 'Your new OTP code — AI Resume Builder'
            message = f'''Hello {user.get_full_name()},

A new OTP has been requested for your password reset process.

Your 6-digit OTP code is: {new_otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Best regards,
AI Resume Builder Team
'''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            # Store sent time so frontend can show cooldown
            request.session['password_reset_sent_at'] = timezone.now().isoformat()
            # Mark just-sent so the banner can be shown on next interaction
            request.session['password_reset_just_sent'] = True
            # For local development: expose the OTP in session so developers can test flows
            if getattr(settings, 'DEBUG', False):
                request.session['password_reset_debug_otp'] = new_otp
            logger.info(f"✅ Resent password reset OTP to {email}")
            messages.success(request, 'A new OTP has been sent to your email.')
            return redirect('password_reset_verify_otp')

        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found for this email. Please request a new reset.')
            return redirect('password_reset_request')
        except Exception as e:
            logger.exception(f"❌ Failed to resend password reset OTP: {str(e)}")
            messages.error(request, 'Failed to resend OTP. Please try again later.')
            return redirect('password_reset_verify_otp')


class ClearPasswordResetJustSentView(View):
    """AJAX endpoint to clear the 'password_reset_just_sent' session flag.

    This allows the frontend to notify the server that the banner was shown
    to the user so it doesn't reappear on subsequent navigations.
    """

    def post(self, request):
        request.session.pop('password_reset_just_sent', None)
        return JsonResponse({'ok': True})
