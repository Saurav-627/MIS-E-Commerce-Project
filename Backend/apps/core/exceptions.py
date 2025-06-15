from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data,
            'status_code': response.status_code
        }

        # Log the error
        logger.error(f"API Error: {exc} - Context: {context}")

        # Customize error messages based on status code
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Bad request'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data['message'] = 'Method not allowed'
        elif response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            custom_response_data['message'] = 'Internal server error'

        response.data = custom_response_data

    return response