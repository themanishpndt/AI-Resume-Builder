from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import random
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses email as the primary authentication field.
    Supports both email and username for flexibility.
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # EMAIL as primary field but support username too
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Allow both email and username login
    def clean(self):
        super().clean()
        # Ensure username is unique
        if self.username:
            qs = CustomUser.objects.filter(username=self.username)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValueError(f"Username '{self.username}' is already taken.")
        
        # Check if email was recently deleted
        if self.email and not self.pk:  # Only check for new users
            if DeletedEmail.is_email_deleted(self.email):
                raise ValidationError(
                    "This email was recently used for a deleted account. "
                    "Please use a different email or wait 30 days."
                )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        # Some deployments (or older user rows) may not have a `deleted_at` attribute
        # on the user instance. Guard with getattr to avoid AttributeError in admin
        # pages and elsewhere where str(obj) is called.
        deleted_at = getattr(self, 'deleted_at', None)
        if deleted_at:
            try:
                return f"{self.email} (deleted on {deleted_at.strftime('%Y-%m-%d')})"
            except Exception:
                # If formatting fails for any reason, fall back to the email
                return self.email
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class DeletedEmail(models.Model):
    """
    Model to store deleted emails for a certain period.
    """
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def is_email_deleted(cls, email):
        """
        Check if an email was recently deleted.
        """
        if not email:
            return False
        # Normalize to lower-case for consistent comparisons
        email_lc = email.lower()
        qs = cls.objects.filter(email=email_lc)
        if qs.exists():
            deleted_at = qs.first().deleted_at
            if (timezone.now() - deleted_at).days < 30:
                return True
        return False


@receiver(post_delete, sender=CustomUser)
def create_deleted_email(sender, instance, **kwargs):
    """
    Signal to create a DeletedEmail record when a user is deleted.
    """
    # Avoid raising IntegrityError if a DeletedEmail for this address
    # already exists. Use get_or_create to be idempotent.
    if instance.email:
        try:
            DeletedEmail.objects.get_or_create(email=instance.email.lower())
        except Exception:
            # Be resilient: if something unexpected happens (race
            # condition or DB error), don't break the user deletion
            # flow. We intentionally swallow the error but log if a
            # logging system is present.
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Failed to record deleted email for %s", instance.email)


class SignupOTP(models.Model):
    """
    Model to store OTP for email verification during signup.
    OTP expires after 10 minutes for user convenience.
    """
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=128)  # Hashed password
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Signup OTP'
        verbose_name_plural = 'Signup OTPs'
    
    def __str__(self):
        return f"Signup OTP for {self.email} - {self.otp}"
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not verified)."""
        if self.is_verified:
            return False
        expiry_time = self.created_at + timedelta(minutes=10)
        return timezone.now() < expiry_time
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP."""
        return str(random.randint(100000, 999999))


class PasswordResetOTP(models.Model):
    """
    Model to store OTP for password reset.
    OTP expires after 10 minutes for user convenience.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='password_reset_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
    
    def __str__(self):
        return f"OTP {self.otp} for {self.user.email}"
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)."""
        if self.is_used:
            return False
        expiry_time = self.created_at + timedelta(minutes=10)
        return timezone.now() < expiry_time
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP."""
        return str(random.randint(100000, 999999))
