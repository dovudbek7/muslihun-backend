import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = _convert_django_validation_error(exc)

    if isinstance(exc, IntegrityError):
        return Response(
            {'error': 'Database integrity error', 'detail': str(exc)},
            status=status.HTTP_409_CONFLICT,
        )

    response = exception_handler(exc, context)

    if response is not None:
        response.data = _normalize_error_response(response.data, response.status_code)

    if response is None:
        logger.exception('Unhandled exception: %s', exc)
        return Response(
            {'error': 'Internal server error', 'detail': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _normalize_error_response(data, status_code):
    if isinstance(data, dict) and 'detail' in data:
        return {'error': str(data['detail']), 'status_code': status_code}
    if isinstance(data, dict):
        return {'error': 'Validation failed', 'fields': data, 'status_code': status_code}
    return {'error': str(data), 'status_code': status_code}


def _convert_django_validation_error(exc):
    from rest_framework.exceptions import ValidationError
    if hasattr(exc, 'message_dict'):
        detail = exc.message_dict
    elif hasattr(exc, 'messages'):
        detail = exc.messages
    else:
        detail = str(exc)
    return ValidationError(detail=detail)
