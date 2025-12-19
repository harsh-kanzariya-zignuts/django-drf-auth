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
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import UpdateUserSerializer, UserSerializer

from .serializers import (
    ChangePasswordSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password", "access_token")
)


class GoogleLogin(SocialLoginView):
    """
    Google OAuth2 Login
    POST /api/auth/social/google/
    Body: {"access_token": "..."}
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client


class FacebookLogin(SocialLoginView):
    """
    Facebook OAuth2 Login
    POST /api/auth/social/facebook/
    Body: {"access_token": "..."}
    """

    adapter_class = FacebookOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client


class GitHubLogin(SocialLoginView):
    """
    GitHub OAuth2 Login
    POST /api/auth/social/github/
    Body: {"access_token": "..."}
    """

    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client


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
            return Response(
                {
                    "error": "cannot_disconnect",
                    "message": "Cannot disconnect the only login method. "
                    "Please set a password first.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            account = social_accounts.get(provider=provider)
            account.delete()

            logger.info(
                f"User {user.email} (ID: {user.id}) disconnected {provider} account"
            )

            return Response(
                {"message": f"{provider.title()} account disconnected successfully"},
                status=status.HTTP_200_OK,
            )

        except SocialAccount.DoesNotExist:
            return Response(
                {
                    "error": "not_found",
                    "message": f"No {provider} account is connected",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user profile
    GET /api/auth/profile/
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


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
            return Response(
                {"error": "invalid_password", "message": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user.set_password(serializer.validated_data["new_password"])

        # Track who changed the password
        user.updated_by = user  # Self-update
        user.save()

        logger.info(f"Password changed for user: {user.email} (ID: {user.id})")

        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


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
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        logger.info(f"User logged out: {request.user.email} (ID: {request.user.id})")

        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
