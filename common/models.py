import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .managers import AllObjectsManager, BaseManager


class BaseModel(models.Model):
    """
    Abstract base model that provides:
    - UUID primary key
    - Automatic created/updated/deleted tracking
    - Soft delete support
    - Audit trail (who created/updated/deleted)

    Usage:
        class Product(BaseModel):
            name = models.CharField(max_length=100)

        # In views/services:
        product.save(user=request.user)
        product.soft_delete(user=request.user)
        product.restore(user=request.user)
    """

    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Creation tracking
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        editable=False,
    )

    # Update tracking
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        editable=False,
    )

    # Deletion tracking
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_deleted",
        editable=False,
    )

    # Status flags
    is_active = models.BooleanField(default=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    # Custom managers
    objects = BaseManager()  # Default: only active records
    all_objects = AllObjectsManager()  # All records including deleted

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["-created_at"]),
        ]

    def soft_delete(self, user=None):
        """
        Soft delete: marks record as deleted without removing from database.

        Args:
            user: The user performing the deletion (optional but recommended)

        Example:
            product.soft_delete(user=request.user)
        """
        self.is_active = False
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=["is_active", "is_deleted", "deleted_at", "deleted_by"])

    def restore(self, user=None):
        """
        Restores a soft-deleted record.

        Args:
            user: The user performing the restoration (optional but recommended)

        Example:
            product.restore(user=request.user)
        """
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

    def save(self, *args, **kwargs):
        """
        Override save to automatically set audit fields.

        Usage:
            # Automatically track who created/updated
            product.save(user=request.user)
        """
        user = kwargs.pop("user", None)

        # Set created_by only on new records
        if not self.pk and user and not self.created_by:
            self.created_by = user

        # Always update updated_by when user is provided
        if user:
            self.updated_by = user

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"
