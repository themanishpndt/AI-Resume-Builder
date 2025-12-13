"""
Custom authentication backend to support both email and username login.

Improvements:
- Accept `login` as a fallback key (allauth may pass 'login' instead of 'username').
- Handle MultipleObjectsReturned by using filter().first() to avoid unhandled exceptions
  when duplicate records exist (which previously caused a 500).
- Add logging for easier diagnostics in production.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Allow users to authenticate with either email or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using email or username.

        Note: allauth sometimes sends the value under the key 'login' instead of
        'username', so we accept that as a fallback. Also handle MultipleObjectsReturned
        by falling back to the first matching user.
        """
        # Accept alternate kwarg keys used by some auth libraries
        login_value = username or kwargs.get('login') or kwargs.get('email')

        if not login_value:
            return None

        try:
            # Prefer a single get(), but guard against duplicates
            try:
                user = User.objects.get(Q(username=login_value) | Q(email=login_value))
            except MultipleObjectsReturned:
                # If multiple users match (shouldn't happen with unique emails), pick the first
                logger.warning(
                    "Multiple users found for login value=%s. Falling back to first().",
                    login_value,
                )
                user = User.objects.filter(Q(username=login_value) | Q(email=login_value)).first()

            if not user:
                return None

        except User.DoesNotExist:
            return None
        except Exception as e:
            # Log unexpected exceptions and return None (avoid 500s)
            logger.exception("Unexpected error in EmailOrUsernameBackend.authenticate: %s", e)
            return None

        # Check password and ensure user is allowed to authenticate
        try:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception as e:
            logger.exception("Error checking password for user id=%s: %s", getattr(user, 'pk', None), e)

        return None

    def get_user(self, user_id):
        """
        Get user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
