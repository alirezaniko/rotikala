from django.db import models
from users.models import UserAddress  # , CustomUser as User
from django_jalali.db import models as jmodels
from products.models import Product
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_cart", verbose_name="کاربر")
    total_price = models.IntegerField(verbose_name="مبلغ کل")
    is_paid = models.BooleanField(default=False, verbose_name="وضعیت پرداخت ")
    addresses = models.ManyToManyField(UserAddress, blank=True, related_name='orders', verbose_name='آدرس‌')
    accepted = models.BooleanField(default=False, blank=True, verbose_name='تایید سفارش')
    sended = models.BooleanField(default=False, blank=True, verbose_name='ارسال شده')
    created = jmodels.jDateTimeField(auto_now_add=True, null=True, blank=True)
    delivered = models.BooleanField(default=False, blank=True, verbose_name='تحویل داده شده')
    returned = models.BooleanField(default=False, blank=True, verbose_name='مرجوعی')
    Cancellation = models.BooleanField(default=False, blank=True, verbose_name='لغو شده')
    shipping_cost = models.PositiveIntegerField(default=100000)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

