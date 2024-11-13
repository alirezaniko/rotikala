from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Coupon
from django.utils import timezone


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']


class CouponSerializer(serializers.ModelSerializer):
    code = serializers.CharField(
        max_length=50,
        error_messages={
            'max_length': 'کد تخفیف نباید بیش از ۵۰ کاراکتر باشد.',
            'blank': 'کد تخفیف نمی‌تواند خالی باشد.',
        }
    )
    discount_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        error_messages={
            'max_digits': 'بیش از ۵ رقم برای درصد تخفیف مجاز نیست.',
            'max_decimal_places': 'حداکثر تعداد ارقام اعشار باید ۲ باشد.'
        }
    )

    # تعریف فیلدهای تاریخ با فرمت سفارشی
    valid_from = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M",
        input_formats=["%Y-%m-%d %H:%M"],
        error_messages={
            'invalid': 'تاریخ شروع باید با فرمت YYYY-MM-DD HH:MM وارد شود.'
        }
    )
    valid_to = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M",
        input_formats=["%Y-%m-%d %H:%M"],
        error_messages={
            'invalid': 'تاریخ پایان باید با فرمت YYYY-MM-DD HH:MM وارد شود.'
        }
    )

    max_usage = serializers.IntegerField(
        error_messages={
            'max_value': 'تعداد مجاز استفاده نباید بیشتر از ۹۲۲۳۳۷۲۰۳۶۸۵۴۷۷۵۸۰۷ باشد.',
            'invalid': 'تعداد مجاز استفاده باید یک عدد صحیح باشد.'
        }
    )
    used_count = serializers.IntegerField(
        error_messages={
            'max_value': 'تعداد استفاده شده نباید بیشتر از ۹۲۲۳۳۷۲۰۳۶۸۵۴۷۷۵۸۰۷ باشد.',
            'invalid': 'تعداد استفاده شده باید یک عدد صحیح باشد.'
        }
    )

    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'max_usage', 'used_count']


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
