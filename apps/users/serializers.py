# users/serializers.py
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with UUID support"""

    # Use UUIDField to ensure proper serialization
    id = serializers.UUIDField(read_only=True)

    full_name = serializers.ReadOnlyField()
    social_accounts = serializers.SerializerMethodField()

    email_verified = serializers.ReadOnlyField(source="is_email_verified")

    # Audit fields (optional, for admin/debugging)
    created_by_email = serializers.EmailField(
        source="created_by.email", read_only=True, allow_null=True
    )
    updated_by_email = serializers.EmailField(
        source="updated_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "avatar",
            "bio",
            "is_active",
            "email_verified",
            "created_at",
            "updated_at",
            "social_accounts",
            # Optional audit fields
            "created_by_email",
            "updated_by_email",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "email_verified",
            "created_at",
            "updated_at",
            "created_by_email",
            "updated_by_email",
        ]

    def get_social_accounts(self, obj):
        """Get list of connected social accounts"""
        accounts = SocialAccount.objects.filter(user=obj)
        return [
            {
                "provider": acc.provider,
                "uid": acc.uid,
                "date_joined": acc.date_joined,
            }
            for acc in accounts
        ]


class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "bio", "avatar"]

    def update(self, instance, validated_data):
        """Track who updated the profile"""
        request = self.context.get("request")

        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Set updated_by before save
        if request and request.user:
            instance.updated_by = request.user

        # Save with specific fields to avoid triggering auto_now
        instance.save(
            update_fields=list(validated_data.keys()) + ["updated_by", "updated_at"]
        )

        return instance


class MinimalUserSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested relationships"""

    id = serializers.UUIDField(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "avatar"]
        read_only_fields = fields
