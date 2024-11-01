from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.db.models import Q

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'email', 'password', 'password_confirm')

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        username = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        errors = []

        if User.objects.filter(username=username).exists():
            errors.append('کاربر با این نام کاربری قبلاً ثبت شده است.')

        if User.objects.filter(phone_number=phone_number).exists():
            errors.append('کاربر با این شماره تلفن قبلاً ثبت شده است.')

        if User.objects.filter(email=email).exists():
            errors.append('کاربر با این ایمیل قبلاً ثبت شده است.')

        if len(username) > 248:
            errors.append('تعداد کاراکترهای نام کاربری نباید بیشتر از 248 کاراکتر باشد.')

        if len(phone_number) != 11:
            errors.append('شماره موبایل باید 11 رقم باشد.')

        if password == email:
            errors.append('رمز عبور نباید با ایمیل برابر باشد.')

        if len(password) > 248 or len(password_confirm) > 248:
            errors.append('تعداد کاراکترهای رمز عبور باید کمتر از 248 کاراکتر باشد.')

        if password != password_confirm:
            errors.append('رمز عبور و تایید رمز عبور باید برابر باشند.')

        if len(password) < 8:
            errors.append('رمز عبور باید بیشتر از 8 کاراکتر باشد.')

        if not (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in '@$!%*?&' for c in password)):
            errors.append(
                'رمز عبور باید شامل حروف بزرگ و کوچک، اعداد و حداقل یکی از نمادهای خاص مانند @، %، *، !، & باشد.')

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        errors = []

        if username and password:
            try:
                user = User.objects.get(Q(username=username) | Q(email=username) | Q(phone_number=username))
            except User.DoesNotExist:
                errors.append('نام کاربری یا رمز عبور اشتباه است')
                raise serializers.ValidationError(errors)
            except User.MultipleObjectsReturned:
                errors.append('چندین حساب کاربری با این مشخصات یافت شد')
                raise serializers.ValidationError(errors)

            if not user.check_password(password):
                errors.append('رمز عبور اشتباه است')
                raise serializers.ValidationError(errors)

        else:
            errors.append('یاید نام کاربری و رمز عبور را وارد کنید')
            raise serializers.ValidationError(errors)

        attrs['user'] = user
        return attrs
