from rest_framework import generics, status, permissions, mixins
from rest_framework.response import Response
from rest_framework.request import Request
from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, ApplyCouponSerializer, CouponSerializer
from api.mixins import StandardResponseMixin
from rest_framework.permissions import IsAuthenticated
from products.models import Product, Coupon
from rest_framework.views import APIView
from django.utils import timezone


class AddToCartView(StandardResponseMixin, generics.GenericAPIView):
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return self.error_response(errors=['محصول مورد نظر وجود ندارد'])

        if product.NumberOfProduct <= 0:
            return self.error_response(errors=['محصول دیگر در انبار موجود نیست'])

        user_cart_items = CartItem.objects.filter(cart__user=user, product=product)
        total_quantity_in_cart = sum(item.quantity for item in user_cart_items)

        if total_quantity_in_cart + quantity > product.MaximumBuy and product.MaximumBuy is not None:
            return self.error_response(errors=['تعداد مورد نظر از حداکثر تعداد مجاز بیشتر است'])

        if quantity > product.NumberOfProduct:
            return self.error_response(errors=['تعداد درخواستی از موجودی بیشتر است'])

        cart, created = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        product.NumberOfProduct -= quantity
        product.save()

        return self.success_response(data=['محصول به سبد خرید اضافه شد'], user=request.user)


class RemoveFromCartView(StandardResponseMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product')

        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return self.success_response(data=['"محصول از سبد خرید حذف شد"'])
        except Cart.DoesNotExist:
            return self.error_response(errors=['سبد خرید پیدا نشد'])
        except CartItem.DoesNotExist:
            return self.error_response(errors=['محصول در سبد خرید پیدا نشد'])


class CartDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            cart = Cart.objects.get(user=user)
            return cart
        except Cart.DoesNotExist:
            return self.error_response(errors=['سبد خرید پیدا نشد'])

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        if isinstance(cart, Response):
            return cart
        serializer = self.get_serializer(cart)
        return self.success_response(data=serializer.data, user=request.user)


class ApplyCouponView(StandardResponseMixin, APIView):
    def post(self, request, order_id):
        serializer = ApplyCouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data['code']
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                coupon = Coupon.objects.get(code=coupon_code)

                if coupon.is_valid():
                    order.coupon = coupon
                    order.total_price = order.apply_discount()
                    order.save()

                    coupon.used_count += 1
                    coupon.save()

                    return self.success_response(data=order.total_price, user=request.user)
                else:
                    return self.error_response(errors="کوپن وجود ندارد یا منقضی شده است",
                                               status_code=status.HTTP_400_BAD_REQUEST)
            except Order.DoesNotExist:
                return self.error_response(errors="سفارش وجود ندارد", status_code=status.HTTP_404_NOT_FOUND)
            except Coupon.DoesNotExist:
                return self.error_response(errors="کوپن وجود ندارد", status_code=status.HTTP_404_NOT_FOUND)

        return self.error_response(errors=['کوپن مد نظر وجود ندارد'], status_code=status.HTTP_400_BAD_REQUEST)


class CouponCreateView(StandardResponseMixin, generics.CreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(data=serializer.data, user=request.user)
        errors = serializer.errors.get('non_field_errors', serializer.errors)
        if isinstance(errors, dict):
            errors = sum(errors.values(), [])
        return self.error_response(errors=errors)

