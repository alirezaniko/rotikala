from rest_framework import serializers
from .models import Attribute, Product, ProductAttribute, Tag, Category, Image, Comment, Favorite, SearchHistory, \
    CommentLikeDislike
from django.contrib.auth import get_user_model

User = get_user_model()


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ['attribute', 'value']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['user', 'created_at']


class ReplySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'product', 'author', 'text', 'created_at', 'updated_at', 'replies', 'is_admin_reviewed',
                  'likes_count', 'dislikes_count',
                  'is_visible']
        read_only_fields = ['created_at', 'updated_at', 'replies']

    def get_likes_count(self, obj):
        return obj.likes_dislikes.filter(value=CommentLikeDislike.LIKE).count()

    def get_dislikes_count(self, obj):
        return obj.likes_dislikes.filter(value=CommentLikeDislike.DISLIKE).count()

    def validate_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("محصول مورد نظر وجود ندارد.")
        return value


# class CommentSerializer(serializers.ModelSerializer):
#     likes_count = serializers.SerializerMethodField()
#     dislikes_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Comment
#         fields = ['id', 'text', 'likes_count', 'dislikes_count', 'author']
#
#     def get_likes_count(self, obj):
#         return obj.likes_dislikes.filter(value=CommentLikeDislike.LIKE).count()
#
#     def get_dislikes_count(self, obj):
#         return obj.likes_dislikes.filter(value=CommentLikeDislike.DISLIKE).count()


class ProductSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(source='product_attributes', many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    tag = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    Route = serializers.SerializerMethodField()
    comment_ids = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False

    def get_Route(self, obj):
        Route = []
        category = obj.category
        while category:
            Route.append({
                'name': category.name,
                'slug': category.slug,
            })
            category = category.parent

        return list(reversed(Route))

    def get_comment_ids(self, obj):
        comments = Comment.objects.filter(product=obj, is_visible=True, is_admin_reviewed=True)
        return comments.values_list('id', flat=True)

    class Meta:
        model = Product
        fields = ['id', 'nameFa', 'nameEn', 'description', 'NumberOfProduct', 'MaximumBuy', 'product_code', 'body',
                  'price', 'discount', 'images', 'created_at', 'updated_at', 'tag', 'slug', 'sold', 'view',
                  'attributes', 'is_favorited', 'Route', 'comment_ids']


class RelatedProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'images']

    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        request = self.context.get('request')
        if obj.images.exists():
            image_url = obj.images.first().image.url
            return request.build_absolute_uri(image_url) if request else image_url
        return None


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    sub = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'image', 'slug', 'show_in_home', 'show_in_home_no_product', 'products', 'sub']


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['term', 'created_at']


class HotSearchSerializer(serializers.Serializer):
    term = serializers.CharField()
    count = serializers.IntegerField()
