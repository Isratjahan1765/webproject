from django.contrib import admin
from .models import Arrival, ArrivalItem


class ArrivalItemInline(admin.TabularInline):
    model = ArrivalItem
    extra = 1
    raw_id_fields = ['product']


@admin.register(Arrival)
class ArrivalAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'driver', 'arrival_date', 'status', 'total_items', 'confirmed_by']
    list_filter = ['status', 'arrival_date']
    search_fields = ['batch_number', 'driver__name']
    inlines = [ArrivalItemInline]
    readonly_fields = ['batch_number', 'confirmed_by', 'confirmed_at']
