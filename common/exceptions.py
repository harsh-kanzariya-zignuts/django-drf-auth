from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {"error": True, "message": str(exc), "details": response.data}
        response.data = custom_response

    return response
