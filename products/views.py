from rest_framework import generics, permissions, mixins, filters, views
from .models import Product, Category, Comment, Favorite, SearchHistory, CommentLikeDislike
from .serializers import ProductSerializer, CategorySerializer, RelatedProductSerializer, CommentSerializer, \
    FavoriteSerializer, SearchHistorySerializer, HotSearchSerializer
from api.mixins import StandardResponseMixin
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from rest_framework.filters import SearchFilter
from django.db.models import Count
from django.utils import timezone


class ProductListView(StandardResponseMixin, generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['category', 'price']

    search_fields = ['nameFa', 'nameEn', 'description', 'tag__title']

    ordering_fields = ['price', 'created_at', 'sold']

    def get_queryset(self):
        queryset = super().get_queryset()

        order_by = self.request.query_params.get('order_by', 'created_at')
        order_type = self.request.query_params.get('order_type', 'asc')

        if order_type == 'desc':
            order_by = f'-{order_by}'

        return queryset.order_by(order_by)

    def list(self, request, *args, **kwargs):
        try:

            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)

            return self.success_response(data=serializer.data, user=request.user)

        except Exception as e:
            return self.error_response(errors=['خطا: {}'.format(str(e))])


class ProductDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            serializer = self.get_serializer(instance)
            related_products = Product.objects.filter(
                category=instance.category
            ).exclude(id=instance.id)[:10]

            related_products_serializer = RelatedProductSerializer(related_products, many=True,
                                                                   context={'request': request})

            response_data = {
                'product': serializer.data,
                'related_products': related_products_serializer.data
            }

            return self.success_response(data=response_data, user=request.user)
        except:
            return self.error_response(errors=['محصول وجود ندارد'])


class CategoryListView(StandardResponseMixin, generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, user=request.user)


class CategoryDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(data=serializer.data, user=request.user)
        except Exception:
            return self.error_response(errors=['خطا'])


class FavoriteListView(generics.ListAPIView, StandardResponseMixin):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = Favorite.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, user=request.user)


class AddToFavoritesView(StandardResponseMixin, generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return self.error_response(errors=["محصول مورد نظر پیدا نشد"])

        if Favorite.objects.filter(user=request.user, product=product).exists():
            return self.error_response(errors=["این محصول از قبل در علاقه‌مندی‌های شما وجود دارد"])

        Favorite.objects.create(user=request.user, product=product)
        return self.success_response(data={"message": "محصول به علاقه‌مندی‌ها اضافه شد"}, user=request.user)


class FavoriteDeleteView(StandardResponseMixin, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def delete(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            response = self.destroy(request, *args, **kwargs)
            return self.success_response(data=['محصول حذف شد'], user=request.user)
        except Exception:
            return self.error_response(errors=['محصول وجود ندارد'])


class CommentListCreateView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Comment.objects.filter(product_id=product_id, is_visible=True, is_admin_reviewed=True)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        parent_id = self.request.data.get('parent')
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        if not self.request.user.is_authenticated:
            raise ValidationError("ورود به سیستم لازم است.")

        serializer.save(author=self.request.user, product=product, parent=parent)

    def list(self, request, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            product_id = self.kwargs.get('product_id')
            if Product.objects.filter(id=product_id):
                return self.success_response(data=serializer.data, user=request.user)
            else:
                return self.error_response(errors=['این محصول وجود ندارد'])

        except Product.DoesNotExist:
            return self.error_response(errors=['خطا'])

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')

        if not Product.objects.filter(id=product_id).exists():
            return self.error_response(errors=["محصول مورد نظر وجود ندارد"])
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(data=None, user=request.user)  #######################
        except ValidationError as e:
            return self.error_response(errors=e.detail)
        except Product.DoesNotExist:
            return self.error_response(errors=['محصول مورد نظر پیدا نشد'])
        except Comment.DoesNotExist:
            return self.error_response(errors=['کامنت مورد نظر وجود ندارد'])
        except Exception as e:
            return self.error_response(errors=[str(e)])


class ProductFilter(django_filters.FilterSet):
    nameFa = django_filters.CharFilter(field_name="nameFa", lookup_expr='icontains')
    nameEn = django_filters.CharFilter(field_name="nameEn", lookup_expr='icontains')
    description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['nameFa','nameEn', 'description', 'category']


class ProductSearchView(StandardResponseMixin, generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['nameFa', 'nameEn', 'description', 'category__name']

    def get(self, request, *args, **kwargs):
        search_terms = {
            'nameFa': request.query_params.get('nameFa', ''),
            'nameEn': request.query_params.get('nameEn', ''),
            'description': request.query_params.get('description', ''),
            'category': request.query_params.get('category', '')
        }

        queryset = self.filter_queryset(self.get_queryset())

        for field, term in search_terms.items():
            if term:
                queryset = queryset.filter(
                    Q(**{f"{field}__icontains": term})
                )

                if request.user.is_authenticated:
                    SearchHistory.objects.create(user=request.user, term=term)

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data)


class RecentSearchView(generics.ListAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).order_by('-created_at')[:10]


class HotSearchView(generics.ListAPIView):
    serializer_class = HotSearchSerializer

    def get_queryset(self):
        return (
            SearchHistory.objects.values('term')
                .annotate(count=Count('term'))
                .order_by('-count')[:10]
        )


class CommentLikeDislikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = request.data.get('comment_id')
        value = request.data.get('value')  # 1 برای لایک و -1 برای دیسلایک

        try:
            comment = Comment.objects.get(id=comment_id)
            like_dislike, created = CommentLikeDislike.objects.get_or_create(
                user=request.user, comment=comment, defaults={'value': value}
            )

            if not created:
                if like_dislike.value == value:
                    like_dislike.delete()
                    return Response({"message": "حذف شد"}, status=status.HTTP_204_NO_CONTENT)
                like_dislike.value = value
                like_dislike.save()

            return Response({"message": "ثبت شد"}, status=status.HTTP_201_CREATED)
        except Comment.DoesNotExist:
            return Response({"error": "کامنت مورد نظر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
