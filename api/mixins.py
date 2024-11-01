from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
from users.models import CustomUser as User


class StandardResponseMixin:
    def get_user_role(self, user):
        if not user or not user.is_authenticated:
            return '5'
        if user.is_superuser:
            return '1'
        elif user.is_staff:
            return '2'
        else:
            had_purchased = Order.objects.filter(user=user).exists()
            if had_purchased:
                return '3'
            return '4'

    def success_response(self, data=None, user=None):
        return Response({
            'is_success': True,
            'data': data,
            'errors': None,
            'userPermission': self.get_user_role(user),
        }, status=status.HTTP_200_OK)

    def error_response(self, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            'is_success': False,
            'data': None,
            'errors': errors
        }, status=status_code)
