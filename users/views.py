from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomAuthTokenSerializer
from api.mixins import StandardResponseMixin
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from orders.models import Order

from .swagger_docs import token_obtain_pair_schema, token_refresh_schema, register_schema

from rest_framework_simplejwt.tokens import AccessToken
from .models import CustomUser as User


class RegisterView(StandardResponseMixin, generics.CreateAPIView):
    serializer_class = RegisterSerializer

    @register_schema
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.success_response(data=None, user=request.user)
        else:
            errors = serializer.errors.get('non_field_errors', serializer.errors)
            if isinstance(errors, dict):
                errors = sum(errors.values(), [])
            return self.error_response(errors=errors, status_code=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(StandardResponseMixin, TokenObtainPairView):
    serializer_class = CustomAuthTokenSerializer

    def get_user_role(self, user):
        if user.is_superuser:
            return '1'
        elif user.is_staff:
            return '2'
        elif user.is_authenticated:
            had_purchased = Order.objects.filter(user=user).exists()
            if had_purchased:
                return '3'
            return '4'
        return '5'

    @token_obtain_pair_schema
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            success_response = {
                'is_success': True,
                'data': data,
                'errors': None,
                'userPermission': self.get_user_role(user)
            }

            return Response(success_response, status=status.HTTP_200_OK)
        else:
            errors = serializer.errors.get('non_field_errors', serializer.errors)
            if isinstance(errors, dict):
                errors = sum(errors.values(), [])
            return self.error_response(errors=errors, status_code=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(StandardResponseMixin, TokenRefreshView):

    def get_user_role(self, user):
        if user.is_superuser:
            return '1'
        elif user.is_staff:
            return '2'
        elif Order.objects.filter(user=user).exists():
            return '3'
        elif user.is_authenticated:
            return '4'
        return '5'

    @token_refresh_schema
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            access_token = str(data['access'])

            decoded_token = AccessToken(access_token)
            user_id = decoded_token['user_id']

            user = User.objects.get(id=user_id)

            success_response = {
                'is_success': True,
                'data': {
                    'access': access_token,
                },
                'errors': None,
                'userPermission': self.get_user_role(user)
            }
            return Response(success_response, status=status.HTTP_200_OK)
        except Exception as e:
            return self.error_response(errors=[str(e)], status_code=status.HTTP_400_BAD_REQUEST)
