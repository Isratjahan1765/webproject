from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'unit', 'unit_price', 'is_active', 'created_at']
    list_filter = ['category', 'unit', 'is_active']
    search_fields = ['name', 'name_bn', 'sku']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['unit_price', 'is_active']
    list_per_page = 20
