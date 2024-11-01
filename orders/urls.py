from django.urls import path
from .views import AddToCartView, RemoveFromCartView, CartDetailView

urlpatterns = [
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
]