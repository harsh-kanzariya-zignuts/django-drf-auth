import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_async_email(self, subject, template_name, context, recipient_list):
    """
    Generic async email sender.

    Args:
        subject: Email subject
        template_name: Path to HTML template
        context: Template context dict
        recipient_list: List of recipient emails
    """
    try:
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

        logger.info(f"Email '{subject}' sent to {recipient_list}")
        return {"status": "success", "recipients": recipient_list}

    except Exception as exc:
        logger.error(f"Failed to send email '{subject}': {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_email, verification_url, user_name):
    """Send email verification link asynchronously."""
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, user_email, reset_url, user_name):
    """Send password reset link asynchronously."""
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, user_email, user_name):
    """Send welcome email after successful registration."""
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
