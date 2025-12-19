from django.core.mail import send_mail
from django.db import transaction

from .models import User


class UserService:
    """Business logic for user operations"""

    @staticmethod
    @transaction.atomic
    def create_user(email: str, password: str, **extra_fields) -> User:
        """
        Create a new user with proper validation
        """
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")

        user = User.objects.create_user(
            email=email,
            password=password,
            username=email.split("@")[0],  # Generate username from email
            **extra_fields,
        )

        # Send welcome email (could be async with Celery)
        UserService.send_welcome_email(user)

        return user

    @staticmethod
    def send_welcome_email(user: User) -> None:
        """Send welcome email to new user"""
        send_mail(
            subject="Welcome to Our Platform",
            message=f"Hello {user.username}, welcome aboard!",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            fail_silently=True,
        )

    @staticmethod
    @transaction.atomic
    def deactivate_user(user: User, reason: str = None) -> User:
        """Deactivate user account"""
        user.is_active = False
        user.save(update_fields=["is_active"])

        # Log deactivation reason
        # Could send notification

        return user
