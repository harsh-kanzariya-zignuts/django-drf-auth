# authentication/views.py
import logging

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import UpdateUserSerializer, UserSerializer
from common.responses import error, success

from .schemas import (
    change_password_schema,
    disconnect_social_schema,
    facebook_login_schema,
    github_login_schema,
    google_login_schema,
    logout_schema,
    profile_get_schema,
    profile_update_schema,
    social_accounts_schema,
)
from .serializers import (
    ChangePasswordSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password", "access_token")
)


@google_login_schema
class GoogleLogin(SocialLoginView):
    """
    Google OAuth2 Login
    POST /api/auth/social/google/
    Body: {"access_token": "..."}
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client


@facebook_login_schema
class FacebookLogin(SocialLoginView):
    """
    Facebook OAuth2 Login
    POST /api/auth/social/facebook/
    Body: {"access_token": "..."}
    """

    adapter_class = FacebookOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client


@github_login_schema
class GitHubLogin(SocialLoginView):
    """
    GitHub OAuth2 Login
    POST /api/auth/social/github/
    Body: {"access_token": "..."}
    """

    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client


@social_accounts_schema
class SocialAccountsView(APIView):
    """
    List connected social accounts
    GET /api/auth/social/accounts/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = SocialAccount.objects.filter(user=request.user)

        data = [
            {
                "id": acc.id,
                "provider": acc.provider,
                "uid": acc.uid,
                "date_joined": acc.date_joined,
                "last_login": acc.last_login,
                "extra_data": {
                    "email": acc.extra_data.get("email"),
                    "name": acc.extra_data.get("name"),
                    "picture": (
                        acc.extra_data.get("picture")
                        or acc.extra_data.get("avatar_url")
                    ),
                },
            }
            for acc in accounts
        ]

        return Response(data)


@disconnect_social_schema
class DisconnectSocialAccountView(APIView):
    """
    Disconnect a social account
    DELETE /api/auth/social/disconnect/<provider>/
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, provider):
        user = request.user
        social_accounts = SocialAccount.objects.filter(user=user)

        # Safety check: prevent locking user out
        if social_accounts.count() == 1 and not user.has_usable_password():
            return error(
                message="Cannot disconnect the only login method. Please set a password first.",
                errors={"provider": "Cannot disconnect the only login method"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            account = social_accounts.get(provider=provider)
            account.delete()

            logger.info(
                f"User {user.email} (ID: {user.id}) disconnected {provider} account"
            )

            return success(
                message=f"{provider.title()} account disconnected successfully"
            )

        except SocialAccount.DoesNotExist:
            return error(
                message=f"No {provider} account is connected",
                errors={"provider": f"{provider} account not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )


@profile_get_schema
class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user profile
    GET /api/auth/profile/
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@profile_update_schema
class UpdateProfileView(generics.UpdateAPIView):
    """
    Update user profile with audit trail
    PATCH /api/auth/profile/update/
    """

    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        """Pass request to serializer for audit trail"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@change_password_schema
class ChangePasswordView(APIView):
    """
    Change user password
    POST /api/auth/change-password/
    """

    permission_classes = [IsAuthenticated]

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Check old password
        if not user.check_password(serializer.validated_data["old_password"]):
            return error(
                message="Old password is incorrect",
                errors={"old_password": "The password you entered is incorrect"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user.set_password(serializer.validated_data["new_password"])

        # Track who changed the password
        user.updated_by = user  # Self-update
        user.save()

        logger.info(f"Password changed for user: {user.email} (ID: {user.id})")

        return success(message="Password changed successfully")


@logout_schema
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout by blacklisting refresh token
    POST /api/auth/logout/
    Body: {"refresh": "refresh_token"}
    """
    try:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return error(
                message="Refresh token is required",
                errors={"refresh": "This field is required"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        logger.info(f"User logged out: {request.user.email} (ID: {request.user.id})")

        return success(message="Successfully logged out")
    
    except TokenError as e:
        return error(
            message="Invalid or expired refresh token",
            errors={"detail": str(e)},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        return error(
            message="Logout failed",
            errors={"detail": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
