from django.contrib import admin
from .models import MonthlyReport

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['product', 'year', 'month', 'total_arrived', 'total_dispatched', 'total_dispatch_value']
    list_filter = ['year', 'month']
    search_fields = ['product__name']
