from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for UUID-based User model"""

    list_display = [
        "email",
        "username",
        "full_name",
        "is_active",
        "is_staff",
        "created_at",
    ]
    list_filter = [
        "is_staff",
        "is_superuser",
        "is_active",
        "is_deleted",
        "created_at",
    ]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "phone",
                    "bio",
                    "avatar",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
        (
            _("Audit Trail"),
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "deleted_by",
                    "deleted_at",
                    "is_deleted",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "created_by",
        "updated_by",
        "deleted_by",
        "last_login",
        "date_joined",
    ]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Track who created/updated in admin"""
        if not change:  # Creating new user
            obj.created_by = request.user
        else:  # Updating existing user
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)
