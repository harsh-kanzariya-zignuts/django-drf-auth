# users/models.py
import uuid

from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.managers import AllObjectsManager

from .managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User model with UUID primary key and full audit trail.
    """

    # Override default AutoField id with UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Custom user fields
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)

    # Remove username requirement (make it optional)
    username = models.CharField(max_length=150, blank=True, null=True)

    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Self-referential audit trail
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_created",
        editable=False,
        help_text="User who created this account (null for self-registration)",
    )
    updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_updated",
        editable=False,
        help_text="User who last updated this account",
    )
    deleted_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_deleted",
        editable=False,
        help_text="User who deleted/banned this account",
    )

    # Soft delete flag
    is_deleted = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Custom managers
    objects = CustomUserManager()  # main required user manager
    all_objects = AllObjectsManager()  # Returns all users including deleted

    # Authentication configuration
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs):
        """
        Override save to track audit trail.

        Usage:
            user.save(user=request.user)  # Tracks who made changes
        """
        user = kwargs.pop("user", None)

        # Use _state.adding to check if new record
        if self._state.adding and user:
            self.created_by = user

        # Always track who updated (if user provided and not creating)
        if user and not self._state.adding:
            self.updated_by = user

        super().save(*args, **kwargs)

    def soft_delete(self, user=None):
        """
        Soft delete: marks user as deleted without removing from database.
        """
        self.is_active = False
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=["is_active", "is_deleted", "deleted_at", "deleted_by"])

    def restore(self, user=None):
        """Restore a soft-deleted user account."""
        self.is_active = True
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        if user:
            self.updated_by = user
        self.save(
            update_fields=[
                "is_active",
                "is_deleted",
                "deleted_at",
                "deleted_by",
                "updated_by",
            ]
        )

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return user's full name or email if name not set"""
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email

    @property
    def is_email_verified(self):
        """
        Returns True if the user's primary email is verified via allauth
        """
        return EmailAddress.objects.filter(user=self, verified=True).exists()

    def get_social_accounts(self):
        """Get connected social accounts"""
        from allauth.socialaccount.models import SocialAccount

        return SocialAccount.objects.filter(user=self)
