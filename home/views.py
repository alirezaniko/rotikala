from django.shortcuts import render
from rest_framework import generics
from products.models import Category
from products.serializers import CategorySerializer


# class CategoryListView(generics.ListAPIView):
#     queryset = Category.objects.filter(parent__isnull=True)  # نمایش فقط دسته‌بندی‌های ریشه
#     serializer_class = CategorySerializer
#
#
# class CategoryDetailView(generics.RetrieveAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer


