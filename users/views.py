from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework import generics, mixins
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
