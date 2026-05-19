import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_async_email(subject, template_name, context, recipient_list):
    """
    Plain helper function to render a template and send an email.

    Not a Celery task — call this from within a @shared_task function
    so retry logic lives in one place (the calling task).

    Args:
        subject: Email subject line
        template_name: Path to the HTML template
        context: Dict of template variables
        recipient_list: List of recipient email addresses

    Returns:
        dict with status and recipients on success

    Raises:
        Exception: Re-raises any send failure so the calling task can retry
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

    logger.info("Email '%s' sent to %s", subject, recipient_list)
    return {"status": "success", "recipients": recipient_list}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_email, verification_url, user_name):
    """Send email verification link asynchronously."""
    try:
        return send_async_email(
            subject="Confirm your email address",
            template_name="account/email/email_confirmation_message.html",
            context={
                "user_name": user_name,
                "verification_url": verification_url,
                "site_name": "Django Auth API",
            },
            recipient_list=[user_email],
        )
    except Exception as exc:
        logger.error("Failed to send verification email to %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, user_email, reset_url, user_name):
    """Send password reset link asynchronously."""
    try:
        return send_async_email(
            subject="Reset your password",
            template_name="account/email/password_reset.html",
            context={
                "user_name": user_name,
                "reset_url": reset_url,
                "site_name": "Django Auth API",
            },
            recipient_list=[user_email],
        )
    except Exception as exc:
        logger.error("Failed to send password reset email to %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, user_email, user_name):
    """Send welcome email after successful email verification."""
    try:
        return send_async_email(
            subject=f"Welcome to Django Auth API, {user_name}!",
            template_name="account/email/welcome.html",
            context={
                "user_name": user_name,
                "site_name": "Django Auth API",
                "support_email": "support@example.com",
            },
            recipient_list=[user_email],
        )
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", user_email, exc)
        raise self.retry(exc=exc)
