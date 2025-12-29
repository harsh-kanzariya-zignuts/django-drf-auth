from rest_framework import status
from rest_framework.response import Response


def success(message, data=None, status_code=status.HTTP_200_OK):
    """
    Standard success response for action endpoints

    Usage:
        return success("User logged out successfully")
        return success("Password updated", data={"email": "user@example.com"})

    DO NOT USE for:
        - List views (use DRF's native pagination)
        - Retrieve views (use DRF's native serializer response)
        - Create/Update views (use DRF's native responses)
    """
    payload = {"message": message}
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status_code)


def error(
    message,
    errors=None,
    status_code=status.HTTP_400_BAD_REQUEST,
):
    """
    Manual error response (rarely needed - exception handler covers most cases)

    Usage:
        return error("Invalid operation", status_code=status.HTTP_403_FORBIDDEN)

    Note: Most validation errors should use raise ValidationError() instead
    """
    payload = {"message": message}
    if errors:
        payload["errors"] = errors
    return Response(payload, status=status_code)
