from drf_spectacular.utils import (
    OpenApiExample,
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

# ==================== Response Serializers ====================


class SuccessResponseSerializer(serializers.Serializer):
    """Standard success response for action endpoints"""

    message = serializers.CharField(help_text="Success message")
    data = serializers.DictField(
        required=False, allow_null=True, help_text="Optional response data"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response"""

    message = serializers.CharField(help_text="Error message")
    errors = serializers.DictField(help_text="Detailed error information")


# ==================== Authentication Schemas ====================

login_schema = extend_schema(
    tags=["Authentication"],
    summary="Login with Email/Password",
    description="Authenticate user and receive JWT access and refresh tokens.",
    responses={
        200: OpenApiResponse(
            description="Successfully authenticated",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                            "full_name": "John Doe",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid credentials",
            examples=[
                OpenApiExample(
                    "Validation Error",
                    value={
                        "message": "Validation failed",
                        "errors": {"non_field_errors": ["Invalid email or password."]},
                    },
                    response_only=True,
                )
            ],
        ),
    },
)

logout_schema = extend_schema(
    tags=["Authentication"],
    summary="Logout",
    description="Blacklist the refresh token to log out the user. Requires authentication.",
    request=inline_serializer(
        name="LogoutRequest",
        fields={
            "refresh": serializers.CharField(
                help_text="JWT refresh token to blacklist", required=True
            ),
        },
    ),
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Successfully logged out",
            examples=[
                OpenApiExample(
                    "Success",
                    value={"message": "Successfully logged out"},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid or missing refresh token",
            examples=[
                OpenApiExample(
                    "Missing Token",
                    value={
                        "message": "Refresh token is required",
                        "errors": {"refresh": "This field is required"},
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Invalid Token",
                    value={
                        "message": "Logout failed",
                        "errors": {"detail": "Token is invalid or expired"},
                    },
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized - Authentication required",
        ),
    },
)

register_schema = extend_schema(
    tags=["Authentication"],
    summary="Register New User",
    description="Create a new user account. Email verification may be required based on settings.",
    responses={
        201: OpenApiResponse(
            description="User created successfully",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "newuser@example.com",
                            "full_name": "John Doe",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Validation error",
            examples=[
                OpenApiExample(
                    "Validation Errors",
                    value={
                        "message": "Validation failed",
                        "errors": {
                            "email": ["A user with this email already exists."],
                            "password": ["This password is too short."],
                        },
                    },
                    response_only=True,
                )
            ],
        ),
    },
)


# ==================== Email Verification Schemas ====================

verify_email_schema = extend_schema(
    tags=["Authentication"],
    summary="Verify Email Address",
    description="Verify user email address using the verification key sent via email.",
    request=inline_serializer(
        name="VerifyEmailRequest",
        fields={
            "key": serializers.CharField(help_text="Email verification key from email")
        },
    ),
    responses={
        200: OpenApiResponse(
            description="Email verified successfully",
            examples=[
                OpenApiExample("Success", value={"detail": "ok"}, response_only=True)
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer, description="Invalid verification key"
        ),
    },
)

resend_email_schema = extend_schema(
    tags=["Authentication"],
    summary="Resend Email Verification",
    description="Resend email verification link to the user's email address.",
    request=inline_serializer(
        name="ResendEmailRequest",
        fields={"email": serializers.EmailField(help_text="User's email address")},
    ),
    responses={
        200: OpenApiResponse(
            description="Verification email sent",
            examples=[
                OpenApiExample("Success", value={"detail": "ok"}, response_only=True)
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Email already verified or invalid",
        ),
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
        200: OpenApiResponse(
            description="New access token generated",
            examples=[
                OpenApiExample(
                    "Success",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",  # If ROTATE_REFRESH_TOKENS is True
                    },
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid or expired refresh token",
            examples=[
                OpenApiExample(
                    "Invalid Token",
                    value={
                        "message": "Token is invalid or expired",
                        "errors": {
                            "detail": "Token is invalid or expired",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
    },
)

token_verify_schema = extend_schema(
    tags=["Token Management"],
    summary="Verify Token",
    description="Check if a JWT token (access or refresh) is valid and not expired.",
    request=inline_serializer(
        name="TokenVerifyRequest",
        fields={
            "token": serializers.CharField(help_text="JWT token to verify"),
        },
    ),
    responses={
        200: OpenApiResponse(
            description="Token is valid",
            examples=[OpenApiExample("Valid Token", value={}, response_only=True)],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Token is invalid or expired",
            examples=[
                OpenApiExample(
                    "Invalid Token",
                    value={
                        "message": "Token is invalid or expired",
                        "errors": {
                            "detail": "Token is invalid or expired",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
    },
)


# ==================== Password Management Schemas ====================

password_reset_schema = extend_schema(
    tags=["Password"],
    summary="Request Password Reset",
    description="Send password reset email to the user's registered email address.",
    request=inline_serializer(
        name="PasswordResetRequest",
        fields={
            "email": serializers.EmailField(
                help_text="User's registered email address"
            ),
        },
    ),
    responses={
        200: OpenApiResponse(
            description="Password reset email sent (always returns success even if email doesn't exist)",
            examples=[
                OpenApiExample(
                    "Success",
                    value={"detail": "Password reset e-mail has been sent."},
                    response_only=True,
                )
            ],
        ),
    },
)

password_reset_confirm_schema = extend_schema(
    tags=["Password"],
    summary="Confirm Password Reset",
    description="Set new password using the reset token received via email.",
    request=inline_serializer(
        name="PasswordResetConfirmRequest",
        fields={
            "new_password1": serializers.CharField(
                help_text="New password", style={"input_type": "password"}
            ),
            "new_password2": serializers.CharField(
                help_text="Confirm new password", style={"input_type": "password"}
            ),
            "uid": serializers.CharField(help_text="Base64 encoded user ID from email"),
            "token": serializers.CharField(help_text="Password reset token from email"),
        },
    ),
    responses={
        200: OpenApiResponse(
            description="Password reset successful",
            examples=[
                OpenApiExample(
                    "Success",
                    value={"detail": "Password has been reset with the new password."},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid token or passwords don't match",
            examples=[
                OpenApiExample(
                    "Invalid Token",
                    value={
                        "message": "Validation failed",
                        "errors": {"token": ["Invalid value"]},
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Password Mismatch",
                    value={
                        "message": "Validation failed",
                        "errors": {
                            "new_password2": ["The two password fields didn't match."]
                        },
                    },
                    response_only=True,
                ),
            ],
        ),
    },
)

change_password_schema = extend_schema(
    tags=["Password"],
    summary="Change Password",
    description="Change authenticated user's password. Requires old password verification.",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Password changed successfully",
            examples=[
                OpenApiExample(
                    "Success",
                    value={"message": "Password changed successfully"},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid old password or validation error",
            examples=[
                OpenApiExample(
                    "Wrong Old Password",
                    value={
                        "message": "Old password is incorrect",
                        "errors": {
                            "old_password": "The password you entered is incorrect"
                        },
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Password Mismatch",
                    value={
                        "message": "Validation failed",
                        "errors": {"new_password": ["Password fields didn't match."]},
                    },
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized - Authentication required",
        ),
    },
)


# ==================== Profile Schemas ====================

profile_get_schema = extend_schema(
    tags=["Profile"],
    summary="Get Current User Profile",
    description="Retrieve authenticated user's complete profile including UUID, email, social accounts, etc.",
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description="User profile data",
            examples=[
                OpenApiExample(
                    "User Profile",
                    value={
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "username": "user",
                        "first_name": "John",
                        "last_name": "Doe",
                        "full_name": "John Doe",
                        "phone": "+1234567890",
                        "avatar": "https://example.com/avatar.jpg",
                        "bio": "Software developer",
                        "is_active": True,
                        "email_verified": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-20T15:45:00Z",
                        "social_accounts": [
                            {
                                "provider": "google",
                                "uid": "123456789",
                                "date_joined": "2024-01-15T10:30:00Z",
                            }
                        ],
                    },
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized - Authentication required",
        ),
    },
)

profile_update_schema = extend_schema(
    tags=["Profile"],
    summary="Update User Profile",
    description="Update user profile fields. Only provided fields will be updated (partial update supported).",
    request=UpdateUserSerializer,
    responses={
        200: OpenApiResponse(
            response=UpdateUserSerializer,
            description="Updated profile data",
            examples=[
                OpenApiExample(
                    "Updated Profile",
                    value={
                        "first_name": "John",
                        "last_name": "Smith",
                        "phone": "+1234567890",
                        "bio": "Updated bio",
                        "avatar": "https://example.com/new-avatar.jpg",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid data",
            examples=[
                OpenApiExample(
                    "Validation Error",
                    value={
                        "message": "Validation failed",
                        "errors": {"phone": ["Enter a valid phone number."]},
                    },
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized - Authentication required",
        ),
    },
)


# ==================== Social Auth Schemas ====================

google_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="Google OAuth Login",
    description="""
    Login or register using Google OAuth2.
    
    Steps:
    1. Obtain access_token from Google OAuth2 flow on frontend
    2. Send access_token to this endpoint
    3. Backend validates token with Google
    4. Returns JWT tokens and user data
    
    If email already exists, connects Google account to existing user.
    If new email, creates new user account.
    """,
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Successfully authenticated",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@gmail.com",
                            "full_name": "John Doe",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid or expired access token",
            examples=[
                OpenApiExample(
                    "Invalid Token",
                    value={
                        "message": "Authentication failed",
                        "errors": {"non_field_errors": ["Incorrect value"]},
                    },
                    response_only=True,
                )
            ],
        ),
    },
)

facebook_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="Facebook OAuth Login",
    description="""
    Login or register using Facebook OAuth2.
    
    Steps:
    1. Obtain access_token from Facebook OAuth2 flow on frontend
    2. Send access_token to this endpoint
    3. Backend validates token with Facebook
    4. Returns JWT tokens and user data
    """,
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Successfully authenticated",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@facebook.com",
                            "full_name": "John Doe",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid or expired access token",
        ),
    },
)

github_login_schema = extend_schema(
    tags=["Social Auth"],
    summary="GitHub OAuth Login",
    description="""
    Login or register using GitHub OAuth2.
    
    Steps:
    1. Obtain access_token from GitHub OAuth2 flow on frontend
    2. Send access_token to this endpoint
    3. Backend validates token with GitHub
    4. Returns JWT tokens and user data
    """,
    request=SocialLoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Successfully authenticated",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@github.com",
                            "full_name": "John Doe",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid or expired access token",
        ),
    },
)

social_accounts_schema = extend_schema(
    tags=["Social Auth"],
    summary="List Connected Social Accounts",
    description="Get all social authentication providers (Google, Facebook, GitHub) connected to the authenticated user's account.",
    responses={
        200: OpenApiResponse(
            description="List of connected social accounts",
            examples=[
                OpenApiExample(
                    "Connected Accounts",
                    value=[
                        {
                            "id": 1,
                            "provider": "google",
                            "uid": "123456789",
                            "date_joined": "2024-01-15T10:30:00Z",
                            "last_login": "2024-01-20T15:45:00Z",
                            "extra_data": {
                                "email": "user@gmail.com",
                                "name": "John Doe",
                                "picture": "https://lh3.googleusercontent.com/...",
                            },
                        },
                        {
                            "id": 2,
                            "provider": "github",
                            "uid": "987654321",
                            "date_joined": "2024-02-01T08:20:00Z",
                            "last_login": "2024-02-10T12:30:00Z",
                            "extra_data": {
                                "email": "user@github.com",
                                "name": "John Doe",
                                "picture": "https://avatars.githubusercontent.com/...",
                            },
                        },
                    ],
                    response_only=True,
                ),
                OpenApiExample("No Accounts", value=[], response_only=True),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized - Authentication required",
        ),
    },
)

disconnect_social_schema = extend_schema(
    tags=["Social Auth"],
    summary="Disconnect Social Account",
    description="""
    Disconnect a social authentication provider from the user's account.
    
    Safety check: Cannot disconnect if it's the only authentication method 
    and user has no password set (would lock user out of account).
    """,
    parameters=[
        OpenApiParameter(
            name="provider",
            type=str,
            location=OpenApiParameter.PATH,
            description="Social provider name",
            enum=["google", "facebook", "github"],
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Account disconnected successfully",
            examples=[
                OpenApiExample(
                    "Success",
                    value={"message": "Google account disconnected successfully"},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Cannot disconnect - it's the only authentication method",
            examples=[
                OpenApiExample(
                    "Only Login Method",
                    value={
                        "message": "Cannot disconnect the only login method. Please set a password first.",
                        "errors": {
                            "provider": "Cannot disconnect the only login method"
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Social account not found",
            examples=[
                OpenApiExample(
                    "Not Found",
                    value={
                        "message": "No google account is connected",
                        "errors": {"provider": "google account not found"},
                    },
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized - Authentication required",
        ),
    },
)
