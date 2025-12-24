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

# ==================== Authentication Schemas ====================

login_schema = extend_schema(
    tags=["Authentication"],
    summary="Login with Email/Password",
    description="Authenticate user and receive JWT access and refresh tokens.",
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid credentials"),
    },
)

logout_schema = extend_schema(
    tags=["Authentication"],
    summary="Logout",
    description="Blacklist the refresh token to log out.",
    request=inline_serializer(
        name="LogoutRequest",
        fields={
            "refresh": serializers.CharField(help_text="JWT refresh token to blacklist"),
        },
    ),
    responses={
        200: OpenApiResponse(description="Successfully logged out"),
        400: OpenApiResponse(description="Invalid refresh token"),
    },
)

register_schema = extend_schema(
    tags=["Authentication"],
    summary="Register New User",
    description="Create a new user account with email verification.",
    responses={
        201: OpenApiResponse(description="User created successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
)


# ==================== Email Verification Schemas ====================

verify_email_schema = extend_schema(
    tags=["Authentication"],
    summary="Verify Email Address",
    description="Verify user email address using the verification key sent via email.",
    responses={
        200: OpenApiResponse(description="Email verified successfully"),
        400: OpenApiResponse(description="Invalid verification key"),
    },
)

resend_email_schema = extend_schema(
    tags=["Authentication"],
    summary="Resend Email Verification",
    description="Resend email verification link to the user's email address.",
    responses={
        200: OpenApiResponse(description="Verification email sent"),
        400: OpenApiResponse(description="Email already verified or invalid"),
    },
)


# ==================== Token Management Schemas ====================

token_refresh_schema = extend_schema(
    tags=["Token Management"],
    summary="Refresh Access Token",
    description="Get a new access token using a valid refresh token.",
    request=inline_serializer(
        name="TokenRefreshRequest",
        fields={
            "refresh": serializers.CharField(help_text="JWT refresh token"),
        },
    ),
    responses={
        200: inline_serializer(
            name="TokenRefreshResponse",
            fields={
                "access": serializers.CharField(help_text="New access token"),
            },
        ),
        401: OpenApiResponse(description="Invalid or expired refresh token"),
    },
)

token_verify_schema = extend_schema(
    tags=["Token Management"],
    summary="Verify Token",
    description="Check if a JWT token is valid.",
    request=inline_serializer(
        name="TokenVerifyRequest",
        fields={
            "token": serializers.CharField(help_text="JWT token (access or refresh)"),
        },
    ),
    responses={
        200: OpenApiResponse(description="Token is valid"),
        401: OpenApiResponse(description="Token is invalid or expired"),
    },
)


# ==================== Password Management Schemas ====================

password_reset_schema = extend_schema(
    tags=["Password"],
    summary="Request Password Reset",
    description="Send password reset email.",
    request=inline_serializer(
        name="PasswordResetRequest",
        fields={
            "email": serializers.EmailField(help_text="User's registered email"),
        },
    ),
    responses={
        200: OpenApiResponse(description="Password reset email sent"),
    },
)

password_reset_confirm_schema = extend_schema(
    tags=["Password"],
    summary="Confirm Password Reset",
    description="Set new password using reset token from email.",
    request=inline_serializer(
        name="PasswordResetConfirmRequest",
        fields={
            "new_password1": serializers.CharField(help_text="New password"),
            "new_password2": serializers.CharField(help_text="Confirm new password"),
            "uid": serializers.CharField(help_text="Base64 encoded user ID"),
            "token": serializers.CharField(help_text="Password reset token"),
        },
    ),
    responses={
        200: OpenApiResponse(description="Password reset successful"),
        400: OpenApiResponse(description="Invalid token or passwords don't match"),
    },
)

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


# ==================== Profile Schemas ====================

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


# ==================== Social Auth Schemas ====================

google_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="Google OAuth Login",
    description="Login or register using Google OAuth2. Provide the access_token obtained from Google.",
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid token"),
    },
)

facebook_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="Facebook OAuth Login",
    description="Login or register using Facebook OAuth2. Provide the access_token obtained from Facebook.",
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid token"),
    },
)

github_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="GitHub OAuth Login",
    description="Login or register using GitHub OAuth2. Provide the access_token obtained from GitHub.",
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(description="Successfully authenticated"),
        400: OpenApiResponse(description="Invalid token"),
    },
)

social_accounts_schema = extend_schema(
    tags=["Social Auth"],
    summary="List Connected Social Accounts",
    description="Get all social accounts (Google, Facebook, GitHub) connected to the user.",
    responses={
        200: OpenApiResponse(
            description="List of connected social accounts",
            response={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "provider": {"type": "string"},
                        "uid": {"type": "string"},
                        "date_joined": {"type": "string", "format": "date-time"},
                    },
                },
            },
        )
    },
)

disconnect_social_schema = extend_schema(
    tags=["Social Auth"],
    summary="Disconnect Social Account",
    description="Disconnect a social account from user profile. Cannot disconnect if it's the only authentication method.",
    parameters=[
        OpenApiParameter(
            name="provider",
            type=str,
            location=OpenApiParameter.PATH,
            description="Provider name",
            enum=["google", "facebook", "github"],
        )
    ],
    responses={
        200: OpenApiResponse(description="Account disconnected"),
        400: OpenApiResponse(description="Cannot disconnect only auth method"),
        404: OpenApiResponse(description="Social account not found"),
    },
)