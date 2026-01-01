import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_tokens():
    """Cleanup expired JWT tokens daily"""
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

    expired_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = OutstandingToken.objects.filter(
        expires_at__lt=expired_date
    ).delete()

    logger.info(f"Cleaned up {deleted_count} expired tokens")
    return {"deleted_count": deleted_count}


@shared_task
def cleanup_unverified_users():
    """Delete users who haven't verified email after 7 days"""
    from allauth.account.models import EmailAddress
    from django.contrib.auth import get_user_model

    User = get_user_model()
    cutoff_date = timezone.now() - timedelta(days=7)

    unverified_emails = EmailAddress.objects.filter(
        verified=False, user__date_joined__lt=cutoff_date
    )

    user_ids = list(unverified_emails.values_list("user_id", flat=True))
    deleted_count, _ = User.objects.filter(id__in=user_ids).delete()

    logger.info(f"Cleaned up {deleted_count} unverified users")
    return {"deleted_count": deleted_count}
