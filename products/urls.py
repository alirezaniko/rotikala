from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryListView, CategoryDetailView, CommentListCreateView, \
    ProductSearchView, FavoriteListView, FavoriteDeleteView, AddToFavoritesView, CommentLikeDislikeView,RecentSearchView,HotSearchView

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    # path('categories/', CategoryListView.as_view(), name='category-list'),
    # path('category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('product/<int:product_id>/comments/', CommentListCreateView.as_view(), name='product-comments'),
    path('product/commentlikedislike/', CommentLikeDislikeView.as_view(), name='comment-like-dislike'),
    path('product/search/', ProductSearchView.as_view(), name='product-search'),
    path('product/recentsearch/',RecentSearchView.as_view(), name='recent-search'),
    path('product/hotsearch/', HotSearchView.as_view(), name='hot-search'),
    path('favorites/', FavoriteListView.as_view(), name='favorite-list-create'),
    path('favorites/<int:pk>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
    path('favorite/add/<int:product_id>/', AddToFavoritesView.as_view(), name='add_to_favorite'),

]
