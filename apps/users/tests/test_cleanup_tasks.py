import pytest
from django.contrib.auth import get_user_model

from apps.users.tasks import (
    cleanup_expired_tokens,
    cleanup_unverified_users,
)

User = get_user_model()


@pytest.mark.django_db
class TestCleanupTasks:
    def test_cleanup_expired_tokens_returns_deleted_count(self):
        """cleanup_expired_tokens returns a dict with deleted_count."""
        result = cleanup_expired_tokens()

        assert "deleted_count" in result
        assert isinstance(result["deleted_count"], int)

    def test_cleanup_expired_tokens_with_no_expired_tokens(self):
        """cleanup_expired_tokens handles empty table gracefully."""
        result = cleanup_expired_tokens()

        # Fresh test DB — no tokens exist yet, should return 0 not raise
        assert result["deleted_count"] >= 0

    def test_cleanup_unverified_users_returns_deleted_count(self):
        """cleanup_unverified_users returns a dict with deleted_count."""
        result = cleanup_unverified_users()

        assert "deleted_count" in result
        assert isinstance(result["deleted_count"], int)

    def test_cleanup_unverified_users_deletes_old_unverified(self, db):
        """cleanup_unverified_users removes users who haven't verified after 7 days."""
        from datetime import timedelta

        from allauth.account.models import EmailAddress
        from django.utils import timezone

        # Create a user who registered 8 days ago without verifying
        old_user = User.objects.create_user(
            email="unverified@example.com",
            password="Test@123",
        )
        # Backdate their join date to 8 days ago
        User.objects.filter(pk=old_user.pk).update(
            date_joined=timezone.now() - timedelta(days=8)
        )
        EmailAddress.objects.create(
            user=old_user,
            email="unverified@example.com",
            verified=False,
            primary=True,
        )

        result = cleanup_unverified_users()

        assert result["deleted_count"] >= 1
        assert not User.objects.filter(email="unverified@example.com").exists()

    def test_cleanup_unverified_users_keeps_recent_unverified(self, db):
        """cleanup_unverified_users keeps users who registered less than 7 days ago."""
        from allauth.account.models import EmailAddress

        # Create a user who just registered (today) — should NOT be deleted
        new_user = User.objects.create_user(
            email="newunverified@example.com",
            password="Test@123",
        )
        EmailAddress.objects.create(
            user=new_user,
            email="newunverified@example.com",
            verified=False,
            primary=True,
        )

        cleanup_unverified_users()

        # Should still exist — registered too recently
        assert User.objects.filter(email="newunverified@example.com").exists()

    def test_cleanup_unverified_users_keeps_verified_users(self, db):
        """cleanup_unverified_users never deletes verified users regardless of age."""
        from datetime import timedelta

        from allauth.account.models import EmailAddress
        from django.utils import timezone

        verified_user = User.objects.create_user(
            email="verified@example.com",
            password="Test@123",
        )
        User.objects.filter(pk=verified_user.pk).update(
            date_joined=timezone.now() - timedelta(days=30)
        )
        EmailAddress.objects.create(
            user=verified_user,
            email="verified@example.com",
            verified=True,  # ← verified, should never be deleted
            primary=True,
        )

        cleanup_unverified_users()

        assert User.objects.filter(email="verified@example.com").exists()
