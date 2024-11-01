from rest_framework.response import Response
from rest_framework import status


class StandardResponseMixin:
    def success_response(self, data=None):
        return Response({
            'is_success': True,
            'data': data,
            'errors': None
        }, status=status.HTTP_200_OK)

    def error_response(self, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            'is_success': False,
            'data': None,
            'errors': errors
        }, status=status_code)
