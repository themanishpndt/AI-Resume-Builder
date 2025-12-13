"""
Complete signup flow with OTP verification.
Step 1: User submits signup form -> OTP sent to email
Step 2: User verifies OTP -> Account created
"""
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django import forms
from users.models import CustomUser, SignupOTP
import logging

logger = logging.getLogger(__name__)


class SignupRequestForm(forms.Form):
    """Form for initial signup request."""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your.email@example.com'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Create a strong password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Re-enter your password'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            # Provide a friendlier and actionable message
            raise forms.ValidationError(
                'An account with this email already exists. Try logging in or use "Forgot password" to reset your password.'
            )
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        if password1 and len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data


class OTPVerificationForm(forms.Form):
    """Form to verify OTP."""
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6',
            'style': 'letter-spacing: 10px; font-size: 24px;'
        })
    )


class SignupRequestView(View):
    """Step 1: User submits signup form and receives OTP."""
    template_name = 'account/signup.html'
    
    def get(self, request):
        form = SignupRequestForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SignupRequestForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password1']
            
            try:
                # Generate OTP
                otp_code = SignupOTP.generate_otp()
                
                # Delete old unverified OTPs for this email
                SignupOTP.objects.filter(email=email, is_verified=False).delete()
                
                # Hash the password before storing
                from django.contrib.auth.hashers import make_password
                hashed_password = make_password(password)
                
                # Create new signup OTP record
                SignupOTP.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password,
                    otp=otp_code
                )
                
                logger.info(f"Signup OTP generated for: {email}")
                
                # Send OTP via email
                subject = 'Verify Your Email - AI Resume Builder'
                message = f'''Hello {first_name} {last_name},

Welcome to AI Resume Builder!

Email Verification — Secure Signup

To complete your registration, please verify your email address using the 6-digit OTP below:

Your OTP code is: {otp_code}

This OTP is valid for 10 minutes.

How it works:
- We generated a one-time, 6-digit code and sent it to this email address.
- Enter the code on the verification page to confirm your email and activate your account.

Security tip:
Never share this code. We will never ask for your password via email.

If you did not create an account, please ignore this email.

Best regards,
AI Resume Builder Team
'''
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    logger.info(f"✅ Signup OTP email sent successfully to {email}")
                    
                    # Store email in session for OTP verification
                    request.session['signup_email'] = email
                    
                    messages.success(
                        request,
                        f'A verification code has been sent to {email}. The code is valid for 10 minutes. Please check your inbox and enter the OTP to complete registration.'
                    )
                    return redirect('signup_verify_otp')
                    
                except Exception as e:
                    logger.error(f"❌ Failed to send signup OTP email to {email}: {str(e)}")
                    
                    if 'console' in settings.EMAIL_BACKEND.lower():
                        messages.warning(
                            request,
                            f'Email backend is set to console. Check server logs for OTP: {otp_code}'
                        )
                        request.session['signup_email'] = email
                        return redirect('signup_verify_otp')
                    else:
                        messages.error(
                            request,
                            'Failed to send verification email. Please check your email configuration.'
                        )
                        return render(request, self.template_name, {'form': form})
                
            except Exception as e:
                logger.exception(f"❌ Unexpected error during signup: {str(e)}")
                messages.error(request, 'An unexpected error occurred. Please try again.')
                return render(request, self.template_name, {'form': form})
        
        # Form has errors
        return render(request, self.template_name, {'form': form})


class SignupVerifyOTPView(View):
    """Step 2: User verifies OTP and account is created."""
    template_name = 'account/signup_verify_otp.html'
    
    def get(self, request):
        # Check if email is in session
        email = request.session.get('signup_email')
        if not email:
            messages.error(request, 'Please start the signup process first.')
            return redirect('account_signup')
        
        form = OTPVerificationForm(initial={'email': email})
        return render(request, self.template_name, {'form': form, 'email': email})
    
    def post(self, request):
        form = OTPVerificationForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = form.cleaned_data['otp']
            
            try:
                # Find the OTP record
                otp_obj = SignupOTP.objects.filter(
                    email=email,
                    otp=otp,
                    is_verified=False
                ).order_by('-created_at').first()
                
                if otp_obj and otp_obj.is_valid():
                    # Create the user account
                    with transaction.atomic():
                        # Generate username from email
                        import re
                        base = email.split('@')[0]
                        base = re.sub(r"[^A-Za-z0-9_.-]", '', base)[:140]
                        username = base
                        suffix = 0
                        
                        while CustomUser.objects.filter(username=username).exists():
                            suffix += 1
                            username = f"{base[:135]}{suffix}"
                        
                        # Create user
                        user = CustomUser.objects.create(
                            username=username,
                            email=email,
                            first_name=otp_obj.first_name,
                            last_name=otp_obj.last_name,
                            password=otp_obj.password,  # Already hashed
                            is_active=True
                        )
                        
                        # Mark OTP as verified
                        otp_obj.is_verified = True
                        otp_obj.save()
                        
                        logger.info(f"✅ User account created successfully: {email}")
                        
                        # Clear session
                        request.session.pop('signup_email', None)
                        
                        messages.success(
                            request,
                            'Account verified successfully! Please log in with your credentials.'
                        )
                        return redirect('account_login')
                else:
                    messages.error(
                        request,
                        'Invalid or expired OTP. Please request a new one.'
                    )
                    logger.warning(f"Invalid OTP attempt for signup: {email}")
                    
            except Exception as e:
                logger.exception(f"❌ Error during OTP verification: {str(e)}")
                messages.error(request, 'An error occurred during verification. Please try again.')
        
        email = request.session.get('signup_email', '')
        return render(request, self.template_name, {'form': form, 'email': email})


class ResendSignupOTPView(View):
    """Resend OTP for signup verification."""
    
    def post(self, request):
        email = request.session.get('signup_email')
        
        if not email:
            messages.error(request, 'Please start the signup process first.')
            return redirect('account_signup')
        
        try:
            # Find the latest unverified OTP
            otp_obj = SignupOTP.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not otp_obj:
                messages.error(request, 'No pending signup found. Please start over.')
                return redirect('account_signup')
            
            # Generate new OTP
            new_otp = SignupOTP.generate_otp()
            otp_obj.otp = new_otp
            otp_obj.created_at = timezone.now()
            otp_obj.save()
            
            # Send new OTP
            subject = 'New Verification Code - AI Resume Builder'
            message = f'''Hello {otp_obj.first_name} {otp_obj.last_name},

Here is your new verification code:

Your OTP code is: {new_otp}

This OTP is valid for 10 minutes.

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
            
            logger.info(f"✅ New signup OTP sent to {email}")
            messages.success(request, 'A new verification code has been sent to your email.')
            
        except Exception as e:
            logger.error(f"❌ Failed to resend OTP: {str(e)}")
            messages.error(request, 'Failed to resend OTP. Please try again.')
        
        return redirect('signup_verify_otp')
