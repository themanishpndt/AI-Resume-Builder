from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from .models import CustomUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resume.countries_data import PHONE_CODES as PHONE_CODE_CHOICES


class CustomSignupForm(SignupForm):
    """
    Custom signup form for django-allauth.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

    def clean_email(self):
        """
        Validate email format and check for existing user.
        Return cleaned email or raise ValidationError with a friendly message.
        """
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Please enter an email address.')

        # Validate proper email format
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Please enter a valid email address.')

        # Check existing user (case-insensitive)
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists. Try logging in instead.')

        return email

    def clean_password1(self):
        """
        Enforce password strength: at least 8 chars, uppercase, lowercase, and number.
        """
        password = self.cleaned_data.get('password1')
        if not password:
            raise forms.ValidationError('Please enter a password.')

        errors = []
        if len(password) < 8:
            errors.append('be at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('include an uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('include a lowercase letter')
        if not re.search(r'\d', password):
            errors.append('include a number')

        if errors:
            raise forms.ValidationError('Password must ' + ', '.join(errors) + '.')

        return password


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    phone_country_code = forms.ChoiceField(
        choices=PHONE_CODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-allow-html': 'true'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (without country code)'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Extract country code from phone if it exists
        if self.instance and self.instance.phone:
            phone = self.instance.phone
            for code, label in PHONE_CODE_CHOICES[1:]:  # Skip empty choice
                if phone.startswith(code):
                    self.initial['phone_country_code'] = code
                    self.initial['phone'] = phone[len(code):].strip()
                    break
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine country code with phone number
        country_code = self.cleaned_data.get('phone_country_code', '')
        phone = self.cleaned_data.get('phone', '')
        if country_code and phone:
            instance.phone = f"{country_code} {phone}"
        elif phone:
            instance.phone = phone
        if commit:
            instance.save()
        return instance
