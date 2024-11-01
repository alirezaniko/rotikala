from rest_framework import generics, status
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from api.mixins import StandardResponseMixin
from rest_framework.permissions import IsAuthenticated
from products.models import Product


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
