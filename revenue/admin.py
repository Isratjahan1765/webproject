from django.contrib import admin
from .models import RevenueEntry

@admin.register(RevenueEntry)
class RevenueEntryAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'unit_price', 'total_amount', 'transaction_date', 'reference']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['product__name', 'reference']
    readonly_fields = ['total_amount']
