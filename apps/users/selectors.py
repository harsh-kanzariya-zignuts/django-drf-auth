from django.db.models import QuerySet

from .models import User


def get_active_users() -> QuerySet[User]:
    """Get all active users"""
    return User.objects.filter(is_active=True)


def get_user_by_email(email: str) -> User | None:
    """Get user by email"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def get_users_with_related_data() -> QuerySet[User]:
    """Get users with optimized queries"""
    return User.objects.select_related("profile").prefetch_related("orders")
