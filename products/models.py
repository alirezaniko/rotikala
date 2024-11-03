from django.db import models
from ckeditor.fields import RichTextField
from django.utils.html import format_html
from django_jalali.db import models as jmodels
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sub')
    image = models.ImageField(blank=True, null=True, upload_to='media/category')
    slug = models.SlugField(blank=True, null=True)
    show_in_home = models.BooleanField(help_text='Are the products of this category displayed on the main page?',
                                       verbose_name='show product in home')
    show_in_home_no_product = models.BooleanField(default=False, verbose_name='show image in home')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def show_image(self):
        if self.image:
            return format_html(f'<img src="{self.image.url}" width="60px" height="50px">')
        return ('no image')


class Image(models.Model):
    product = models.ForeignKey('Product', null=True, on_delete=models.CASCADE,
                                related_name='images_related')
    image = models.ImageField(upload_to='product-img', verbose_name='image')
    alt = models.CharField(max_length=500, null=True, blank=True, verbose_name='image alt')

    class Meta:
        verbose_name = 'image'
        verbose_name_plural = 'images'

    def __str__(self):
        return str(self.image)


class Tag(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.title


class Product(models.Model):
    nameFa = models.CharField(max_length=255)
    nameEn = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    body = models.TextField(null=True)
    price = models.IntegerField()
    discount = models.PositiveIntegerField(null=True, blank=True, verbose_name='discount percent')
    images = models.ManyToManyField(Image, blank=True, related_name='post_images', verbose_name='Product photos')

    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)
    tag = models.ManyToManyField(Tag, blank=True, related_name='post_tag')
    slug = models.SlugField(allow_unicode=True, unique=True)
    sold = models.PositiveIntegerField(default=0, verbose_name='Quantity sold')
    view = models.IntegerField(default=1)
    NumberOfProduct = models.PositiveIntegerField(default=1)
    MaximumBuy = models.PositiveIntegerField(null=True, blank=True)
    product_code = models.CharField(
        max_length=10,
        unique=True,
        editable=False,

    )

    def save(self, *args, **kwargs):
        if not self.product_code:
            last_product = Product.objects.all().order_by('id').last()
            if last_product:
                last_code = int(last_product.product_code)
                self.product_code = '{:04d}'.format(last_code + 1)
            else:
                self.product_code = '0001'
        if not self.MaximumBuy:
            self.MaximumBuy = self.NumberOfProduct
        super(Product, self).save(*args, **kwargs)

    def increase_sold(self, quantity):
        self.sold += quantity
        self.save()

    def show_discount(self):
        if self.discount:
            return (f'yes: %{self.discount}')
        return ('no')

    show_discount.short_description = 'تخفیف'

    def __str__(self):
        return self.nameFa


class Attribute(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, related_name='product_attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.product.nameFa} - {self.attribute.name}: {self.value}'


class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_admin_reviewed = models.BooleanField(default=False, verbose_name="Reviewed by admin")
    is_visible = models.BooleanField(default=False, verbose_name="Visible to users")

    def __str__(self):
        return f"id:{self.id}Comment by {self.author.username} on {self.product.nameFa}"


class CommentLikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes_dislikes')
    value = models.SmallIntegerField(choices=CHOICES)

    class Meta:
        unique_together = ('user', 'comment')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.nameFa}"


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_history")
    term = models.CharField(max_length=255, verbose_name="عبارت جست وجو")
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.term} searched by {self.user}"


class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True, verbose_name='کد تخفیف')
    discount_percentage = models.DecimalField(max_digits=5,decimal_places=2)
    valid_until = models.DateTimeField()
    max_usage = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        from django.utils import timezone
        return self.used_count < self.max_usage and self.valid_until > timezone.now()

    def __str__(self):
        return self.code