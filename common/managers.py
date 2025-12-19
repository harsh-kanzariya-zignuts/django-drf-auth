from django.db import models


class BaseQuerySet(models.QuerySet):
    """Custom QuerySet with soft delete support"""

    def active(self):
        """Return only active, non-deleted records"""
        return self.filter(is_active=True, is_deleted=False)

    def deleted(self):
        """Return only soft-deleted records"""
        return self.filter(is_deleted=True)

    def hard_delete(self):
        """Permanently delete records from database"""
        return super().delete()


class BaseManager(models.Manager.from_queryset(BaseQuerySet)):
    """Manager that filters out deleted records by default"""

    def get_queryset(self):
        """Default queryset returns only active records"""
        return super().get_queryset().active()


class AllObjectsManager(models.Manager.from_queryset(BaseQuerySet)):
    """Manager that returns ALL objects including deleted"""

    def get_queryset(self):
        """Returns all records without filtering"""
        return super().get_queryset()
