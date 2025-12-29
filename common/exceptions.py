"""
Global exception handler for consistent error responses
This catches ALL exceptions and formats them consistently
"""

import logging

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Standardizes all error responses across the API

    Output format:
    {
        "message": "Validation failed",
        "errors": {
            "email": ["This field is required"],
            "password": ["Too short"]
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {"message": get_error_message(exc), "errors": response.data}
        response.data = custom_response
    else:
        # Handle non-DRF exceptions
        if isinstance(exc, Http404):
            from rest_framework.response import Response

            response = Response(
                {
                    "message": "Resource not found",
                    "errors": {"detail": str(exc) or "Not found"},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            from rest_framework.response import Response

            response = Response(
                {
                    "message": "Internal server error",
                    "errors": {"detail": "An unexpected error occurred"},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return response


def get_error_message(exc):
    """Extract user-friendly error message from exception"""
    if isinstance(exc, ValidationError):
        return "Validation failed"
    elif isinstance(exc, AuthenticationFailed):
        return "Authentication failed"
    elif hasattr(exc, "default_detail"):
        return str(exc.default_detail)
    return str(exc) if str(exc) else "An error occurred"
