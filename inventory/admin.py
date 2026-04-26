from django.contrib import admin
from .models import InventoryRecord, InventoryLog

@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_quantity', 'reserved_quantity', 'available_quantity', 'warehouse_location']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['last_restock_date', 'last_dispatch_date']

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'change_type', 'quantity_change', 'quantity_before', 'quantity_after', 'source', 'created_at']
    list_filter = ['change_type']
    search_fields = ['product__name', 'source']
    readonly_fields = ['product', 'change_type', 'quantity_change', 'quantity_before', 'quantity_after', 'source', 'created_at']
