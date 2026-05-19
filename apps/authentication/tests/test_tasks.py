from unittest.mock import call, patch

import pytest
from django.contrib.auth import get_user_model

from apps.authentication.tasks import (
    send_async_email,
    send_password_reset_email_task,
    send_verification_email_task,
    send_welcome_email_task,
)

User = get_user_model()


# Fixtures

@pytest.fixture
def mock_send_mail():
    """Patch send_mail so no real emails are sent in any test."""
    with patch("apps.authentication.tasks.send_mail") as mock:
        yield mock


@pytest.fixture
def mock_render():
    """Patch render_to_string to avoid needing real templates."""
    with patch(
        "apps.authentication.tasks.render_to_string", return_value="<p>Test</p>"
    ) as mock:
        yield mock


# send_async_email (plain helper function)

@pytest.mark.django_db
class TestSendAsyncEmail:
    def test_success_returns_correct_structure(self, mock_render, mock_send_mail):
        """send_async_email returns status and recipients on success."""
        result = send_async_email(
            subject="Test subject",
            template_name="any/template.html",
            context={"user_name": "Harsh"},
            recipient_list=["harsh@example.com"],
        )

        assert result["status"] == "success"
        assert result["recipients"] == ["harsh@example.com"]

    def test_calls_send_mail_with_correct_args(self, mock_render, mock_send_mail):
        """send_async_email passes correct arguments to Django's send_mail."""
        send_async_email(
            subject="Hello",
            template_name="any/template.html",
            context={},
            recipient_list=["a@example.com"],
        )

        mock_send_mail.assert_called_once()
        _, kwargs = mock_send_mail.call_args
        assert kwargs["subject"] == "Hello"
        assert kwargs["recipient_list"] == ["a@example.com"]
        assert kwargs["html_message"] == "<p>Test</p>"
        assert kwargs["fail_silently"] is False

    def test_raises_on_send_mail_failure(self, mock_render, mock_send_mail):
        """send_async_email raises so the calling task can retry."""
        mock_send_mail.side_effect = Exception("SMTP connection refused")

        with pytest.raises(Exception, match="SMTP connection refused"):
            send_async_email(
                subject="Test",
                template_name="any/template.html",
                context={},
                recipient_list=["test@example.com"],
            )

    def test_raises_on_missing_template(self):
        """send_async_email raises TemplateDoesNotExist for invalid templates."""
        from django.template.exceptions import TemplateDoesNotExist

        with pytest.raises(TemplateDoesNotExist):
            send_async_email(
                subject="Test",
                template_name="nonexistent/template.html",
                context={},
                recipient_list=["test@example.com"],
            )

    def test_sends_to_multiple_recipients(self, mock_render, mock_send_mail):
        """send_async_email supports multiple recipients."""
        recipients = ["a@example.com", "b@example.com", "c@example.com"]

        result = send_async_email(
            subject="Bulk",
            template_name="any/template.html",
            context={},
            recipient_list=recipients,
        )

        assert result["recipients"] == recipients
        _, kwargs = mock_send_mail.call_args
        assert kwargs["recipient_list"] == recipients


# send_verification_email_task

@pytest.mark.django_db
class TestSendVerificationEmailTask:
    def test_success(self, mock_render, mock_send_mail):
        """Verification email task completes and returns success."""
        result = send_verification_email_task(
            user_email="test@example.com",
            verification_url="http://localhost:3000/confirm-email/test-token/",
            user_name="Harsh",
        )

        assert result["status"] == "success"
        assert result["recipients"] == ["test@example.com"]

    def test_passes_correct_context(self, mock_render, mock_send_mail):
        """Verification email task passes user_name and verification_url to template."""
        send_verification_email_task(
            user_email="test@example.com",
            verification_url="http://localhost:3000/confirm-email/abc123/",
            user_name="Harsh",
        )

        _, kwargs = mock_render.call_args
        context = kwargs.get("context", mock_render.call_args[0][1])
        assert context["user_name"] == "Harsh"
        assert (
            context["verification_url"] == "http://localhost:3000/confirm-email/abc123/"
        )
        assert context["site_name"] == "Django Auth API"

    def test_retries_on_failure(self, mock_render, mock_send_mail):
        """Verification email task retries when send fails."""
        mock_send_mail.side_effect = Exception("SMTP down")

        # CELERY_TASK_ALWAYS_EAGER + CELERY_TASK_EAGER_PROPAGATES means
        # retries raise immediately in tests rather than re-queuing
        with pytest.raises(Exception):
            send_verification_email_task(
                user_email="test@example.com",
                verification_url="http://localhost:3000/confirm-email/token/",
                user_name="Harsh",
            )


# send_password_reset_email_task

@pytest.mark.django_db
class TestSendPasswordResetEmailTask:
    def test_success(self, mock_render, mock_send_mail):
        """Password reset email task completes and returns success."""
        result = send_password_reset_email_task(
            user_email="test@example.com",
            reset_url="http://localhost:3000/reset-password/test-token/",
            user_name="Harsh",
        )

        assert result["status"] == "success"
        assert result["recipients"] == ["test@example.com"]

    def test_passes_correct_context(self, mock_render, mock_send_mail):
        """Password reset task passes reset_url to template."""
        send_password_reset_email_task(
            user_email="test@example.com",
            reset_url="http://localhost:3000/reset-password/xyz/",
            user_name="Harsh",
        )

        _, kwargs = mock_render.call_args
        context = kwargs.get("context", mock_render.call_args[0][1])
        assert context["reset_url"] == "http://localhost:3000/reset-password/xyz/"
        assert context["user_name"] == "Harsh"

    def test_retries_on_failure(self, mock_render, mock_send_mail):
        """Password reset email task retries when send fails."""
        mock_send_mail.side_effect = Exception("SMTP down")

        with pytest.raises(Exception):
            send_password_reset_email_task(
                user_email="test@example.com",
                reset_url="http://localhost:3000/reset-password/token/",
                user_name="Harsh",
            )


# send_welcome_email_task

@pytest.mark.django_db
class TestSendWelcomeEmailTask:
    def test_success(self, mock_render, mock_send_mail):
        """Welcome email task completes and returns success."""
        result = send_welcome_email_task(
            user_email="test@example.com",
            user_name="Harsh",
        )

        assert result["status"] == "success"
        assert result["recipients"] == ["test@example.com"]

    def test_subject_includes_user_name(self, mock_render, mock_send_mail):
        """Welcome email subject is personalised with the user's name."""
        send_welcome_email_task(
            user_email="test@example.com",
            user_name="Harsh",
        )

        _, kwargs = mock_send_mail.call_args
        assert "Harsh" in kwargs["subject"]

    def test_retries_on_failure(self, mock_render, mock_send_mail):
        """Welcome email task retries when send fails."""
        mock_send_mail.side_effect = Exception("SMTP down")

        with pytest.raises(Exception):
            send_welcome_email_task(
                user_email="test@example.com",
                user_name="Harsh",
            )
