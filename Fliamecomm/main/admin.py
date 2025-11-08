from django.contrib import admin
from .models import Product, Brand, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price')
    search_fields = ('name', 'brand__name', 'category__name')
    list_filter = ('brand', 'category')

admin.site.register(Brand)
admin.site.register(Category)
