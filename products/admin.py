from django.contrib import admin
from .models import Product, Attribute, ProductAttribute, Category, Tag, Image, Comment, Favorite,SearchHistory

admin.site.register(Tag)
admin.site.register(Image)
admin.site.register(Comment)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nameFa', 'price', 'created_at', 'updated_at')
    search_fields = ('nameFa',)
    inlines = [ProductAttributeInline]
    prepopulated_fields = {'slug': ('nameEn',)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Favorite)

admin.site.register(SearchHistory)