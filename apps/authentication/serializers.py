# authentication/serializers.py
from dj_rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.serializers import UserSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that properly handles UUID"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # UUID is automatically converted to string by simplejwt
        # But we explicitly ensure it here for clarity
        token["user_id"] = str(user.id)
        token["email"] = user.email

        return token


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    
    Returns JWT tokens and user data upon successful registration
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ["email", "password", "password2", "first_name", "last_name", "phone"]

    def validate(self, attrs):
        """Validate password match"""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def validate_email(self, value):
        """Ensure email is lowercase and unique"""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def get_cleaned_data(self):
        """
        Required by dj-rest-auth for registration
        Returns cleaned registration data
        """
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password", ""),
            "password2": self.validated_data.get("password2", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "phone": self.validated_data.get("phone", ""),
        }

    def save(self, request):
        """
        Override save to accept request parameter from dj-rest-auth
        This is called by dj_rest_auth.registration.views.RegisterView
        """
        # Get cleaned data
        email = self.validated_data.get("email")
        password = self.validated_data.get("password")
        first_name = self.validated_data.get("first_name", "")
        last_name = self.validated_data.get("last_name", "")
        phone = self.validated_data.get("phone", "")

        # Generate username from email
        username = email.split("@")[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create user (UUID will be auto-generated)
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        # Optional: Track who created this user (for admin registrations)
        if request and hasattr(request, "user") and request.user.is_authenticated:
            user.created_by = request.user
            user.save(update_fields=["created_by"])

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    
    Returns JWT tokens and user data upon successful authentication
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email").lower().strip()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs


class CustomJWTSerializer(BaseJWTSerializer):
    """
    Custom JWT serializer to include full user data in response
    Properly handles UUID fields
    """

    user = serializers.SerializerMethodField()

    class Meta:
        fields = ["access", "refresh", "user"]

    @extend_schema_field(UserSerializer)
    def get_user(self, obj):
        """
        Include full user data in JWT response

        obj contains: {'access': '...', 'refresh': '...', 'user': User instance}
        """
        # Get user from the obj dict (not from request)
        user = obj.get("user")

        if user:
            # Create a new context without the request to avoid AnonymousUser issues
            return UserSerializer(user, context={"request": None}).data

        # Fallback: try to get from request context
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return UserSerializer(request.user, context={"request": None}).data

        return None


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    
    Requires old password verification before setting new password
    """

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        label="Confirm New Password",
    )

    def validate(self, attrs):
        """Validate new password match"""
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class SocialLoginSerializer(serializers.Serializer):
    """
    Serializer for social OAuth login
    
    Accepts access token from OAuth provider
    """
    
    access_token = serializers.CharField(
        required=True,
        help_text="OAuth access token from provider (Google, Facebook, GitHub)"
    )