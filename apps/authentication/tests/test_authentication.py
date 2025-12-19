import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(email="test@yopmail.com", password="Test@123")


@pytest.mark.django_db
class TestAuthentication:
    def test_user_registration(self, api_client):
        """Test user can register with email/password"""
        data = {
            "email": "newuser@example.com",
            "password": "Test@123",
            "password2": "Test@123",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/auth/register/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

        # Verify user exists in database
        user = User.objects.get(email="newuser@example.com")
        assert user.first_name == "New"
        assert user.last_name == "User"

    def test_user_login(self, api_client, test_user):
        """Test user can login"""
        data = {"email": "test@yopmail.com", "password": "Test@123"}  
        response = api_client.post("/api/auth/login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, test_user):
        """Test login fails with wrong password"""
        data = {"email": "test@yopmail.com", "password": "WrongPassword!"}  
        response = api_client.post("/api/auth/login/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_profile_authenticated(self, api_client, test_user):
        """Test authenticated user can get profile"""
        api_client.force_authenticate(user=test_user)
        response = api_client.get("/api/auth/profile/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "test@yopmail.com"  
        assert str(test_user.id) == response.data["id"]

    def test_get_profile_unauthenticated(self, api_client):
        """Test unauthenticated user cannot get profile"""
        response = api_client.get("/api/auth/profile/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, api_client, test_user):
        """Test user can update profile"""
        api_client.force_authenticate(user=test_user)
        data = {"first_name": "Updated", "bio": "New bio"}
        response = api_client.patch("/api/auth/profile/update/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["bio"] == "New bio"

        # Verify audit trail
        test_user.refresh_from_db()
        assert test_user.updated_by == test_user

    def test_change_password(self, api_client, test_user):
        """Test user can change password"""
        api_client.force_authenticate(user=test_user)
        data = {
            "old_password": "Test@123",  
            "new_password": "NewPass456!",
            "new_password2": "NewPass456!",
        }
        response = api_client.post("/api/auth/password/change/", data)

        assert response.status_code == status.HTTP_200_OK

        # Verify new password works
        test_user.refresh_from_db()
        assert test_user.check_password("NewPass456!")

    def test_token_refresh(self, api_client, test_user):
        """Test refresh token works"""
        # Login to get tokens
        login_response = api_client.post(
            "/api/auth/login/",
            {"email": "test@yopmail.com", "password": "Test@123"},
        )
        refresh_token = login_response.data["refresh"]

        # Refresh access token
        response = api_client.post(
            "/api/auth/token/refresh/", {"refresh": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_logout_blacklists_token(self, api_client, test_user):
        """Test logout blacklists refresh token"""
        api_client.force_authenticate(user=test_user)

        # Login to get tokens
        login_response = api_client.post(
            "/api/auth/login/",
            {"email": "test@yopmail.com", "password": "Test@123"},  
        )
        refresh_token = login_response.data["refresh"]

        # Logout
        logout_response = api_client.post(
            "/api/auth/logout/", {"refresh": refresh_token}
        )

        assert logout_response.status_code == status.HTTP_200_OK

        # Try to use blacklisted token
        refresh_response = api_client.post(
            "/api/auth/token/refresh/", {"refresh": refresh_token}
        )

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_soft_delete(self, test_user, db):
        """Test soft delete functionality"""
        admin = User.objects.create_user(
            email="admin@example.com", password="AdminPass123!", is_staff=True
        )

        # Soft delete user
        test_user.soft_delete(user=admin)

        assert test_user.is_deleted is True
        assert test_user.is_active is False
        assert test_user.deleted_at is not None
        assert test_user.deleted_by == admin

        # Verify not in default queryset
        assert not User.objects.filter(email="test@yopmail.com").exists()  
        assert User.all_objects.filter(email="test@yopmail.com").exists()  

    def test_restore_user(self, test_user, db):
        """Test restore soft-deleted user"""
        admin = User.objects.create_user(
            email="admin@example.com", password="AdminPass123!"
        )

        # Soft delete then restore
        test_user.soft_delete(user=admin)
        test_user.restore(user=admin)

        assert test_user.is_deleted is False
        assert test_user.is_active is True
        assert test_user.deleted_at is None
        assert test_user.deleted_by is None
