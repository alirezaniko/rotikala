from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import APIException, AuthenticationFailed, NotAuthenticated


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'درخواست نامعتبر است.'
    default_code = 'invalid'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, CustomValidationError):
        custom_response_data = {
            'is_success': False,
            'data': None,
            'errors': exc.detail
        }
        return Response(custom_response_data, status=exc.status_code)

    if isinstance(exc, (TokenError, InvalidToken)):
        custom_response_data = {
            'is_success': False,
            'data': None,
            'errors': ["توکن نامعتبر است یا مدت زمان آن تمام شده است"]
        }
        return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        custom_response_data = {
            'is_success': False,
            'data': None,
            'errors': ["ورود به سیستم لازم است"]
        }
        return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

    if response is not None:
        custom_response_data = {
            'is_success': False,
            'data': None,
            'errors': response.data
        }
        return Response(custom_response_data, status=response.status_code)

    # return Response({
    #     'is_success': False,
    #     'data': None,
    #     'errors': {
    #         'detail': ['یک خطای ناشناخته رخ داده است.']
    #     }
    # }, status=500)
