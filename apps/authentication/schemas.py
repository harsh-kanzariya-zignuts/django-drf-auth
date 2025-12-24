from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers

from apps.users.serializers import UpdateUserSerializer, UserSerializer

from .serializers import (
    ChangePasswordSerializer,
    SocialLoginSerializer,
)

# Authentication Schemas
logout_schema = extend_schema(
    tags=["Authentication"],
    summary="Logout",
    description="Logout user by blacklisting the refresh token.",
    request=inline_serializer(
        name="LogoutRequest",
        fields={
            "refresh": serializers.CharField(
                help_text="JWT refresh token to blacklist"
            ),
        },
    ),
    responses={
        200: OpenApiResponse(description="Successfully logged out"),
        400: OpenApiResponse(description="Invalid token"),
    },
)


# Profile Schemas
profile_get_schema = extend_schema(
    tags=["Profile"],
    summary="Get Current User Profile",
    description="Retrieve authenticated user's complete profile.",
    responses={200: UserSerializer, 401: OpenApiResponse(description="Unauthorized")},
)

profile_update_schema = extend_schema(
    tags=["Profile"],
    summary="Update User Profile",
    description="Update user profile with audit trail tracking.",
    request=UpdateUserSerializer,
    responses={200: UpdateUserSerializer, 400: OpenApiResponse(description="Invalid data")},
)


# Password Schemas
change_password_schema = extend_schema(
    tags=["Password"],
    summary="Change Password",
    description="Change user password with old password verification.",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(description="Invalid old password"),
    },
)


# Social Auth Schemas
google_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="Google OAuth Login",
    description="Login or register using Google OAuth2.",
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid token"),
    },
)

facebook_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="Facebook OAuth Login",
    description="Login or register using Facebook OAuth2.",
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid token"),
    },
)

github_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="GitHub OAuth Login",
    description="Login or register using GitHub OAuth2.",
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid token"),
    },
)

social_accounts_schema = extend_schema(
    tags=["Social Auth"],
    summary="List Connected Social Accounts",
    description="Get all social accounts connected to the user.",
    responses={200: OpenApiResponse(description="List of social accounts")},
)

disconnect_social_schema = extend_schema(
    tags=["Social Auth"],
    summary="Disconnect Social Account",
    description="Disconnect a social account from user profile.",
    parameters=[
        OpenApiParameter(
            name="provider",
            type=str,
            location=OpenApiParameter.PATH,
            description="Provider name (google, facebook, github)",
            enum=["google", "facebook", "github"],
        )
    ],
    responses={
        200: OpenApiResponse(description="Account disconnected"),
        400: OpenApiResponse(description="Cannot disconnect only auth method"),
        404: OpenApiResponse(description="Social account not found"),
    },
)