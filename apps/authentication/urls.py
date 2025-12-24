# authentication/urls.py
from dj_rest_auth.registration.views import (
    RegisterView,
    ResendEmailVerificationView,
    VerifyEmailView,
)
from dj_rest_auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .schemas import (
    login_schema,
    password_reset_confirm_schema,
    password_reset_schema,
    register_schema,
    resend_email_schema,
    token_refresh_schema,
    token_verify_schema,
    verify_email_schema,
)
from .views import (
    ChangePasswordView,
    DisconnectSocialAccountView,
    FacebookLogin,
    GitHubLogin,
    GoogleLogin,
    SocialAccountsView,
    UpdateProfileView,
    UserProfileView,
    logout_view,
)

# Apply schemas to dj-rest-auth views
RegisterView = register_schema(RegisterView)
VerifyEmailView = verify_email_schema(VerifyEmailView)
ResendEmailVerificationView = resend_email_schema(ResendEmailVerificationView)
LoginView = login_schema(LoginView)
PasswordResetView = password_reset_schema(PasswordResetView)
PasswordResetConfirmView = password_reset_confirm_schema(PasswordResetConfirmView)

# Apply schemas to JWT views
TokenRefreshView = token_refresh_schema(TokenRefreshView)
TokenVerifyView = token_verify_schema(TokenVerifyView)

urlpatterns = [
    # Registration & Email Verification
    path("register/", RegisterView.as_view(), name="rest_register"),
    path("verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"),
    
    # Login/Logout
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", logout_view, name="rest_logout"),

    # Password Management
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
    path("password/change/", ChangePasswordView.as_view(), name="rest_password_change"),

    # JWT Token Management
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # User Profile
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/update/", UpdateProfileView.as_view(), name="update_profile"),

    # Social Authentication
    path("social/google/", GoogleLogin.as_view(), name="google_login"),
    path("social/facebook/", FacebookLogin.as_view(), name="facebook_login"),
    path("social/github/", GitHubLogin.as_view(), name="github_login"),

    # Social account management
    path("social/accounts/", SocialAccountsView.as_view(), name="social_accounts"),
    path("social/disconnect/<str:provider>/", DisconnectSocialAccountView.as_view(), name="social_disconnect"),
]