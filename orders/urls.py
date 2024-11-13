from django.urls import path
from .views import AddToCartView, RemoveFromCartView, CartDetailView,ApplyCouponView,CouponCreateView

urlpatterns = [
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/coupons/create/', CouponCreateView.as_view(), name='coupon-create'),
    path('cart/coupons/apply/', ApplyCouponView.as_view(), name='coupon-apply'),
]