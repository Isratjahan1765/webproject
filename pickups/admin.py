from django.contrib import admin
from .models import Pickup, PickupItem

class PickupItemInline(admin.TabularInline):
    model = PickupItem
    extra = 1
    raw_id_fields = ['product']

@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ['pickup_number', 'driver', 'pickup_date', 'destination', 'status', 'confirmed_by']
    list_filter = ['status', 'pickup_date']
    search_fields = ['pickup_number', 'destination', 'driver__name']
    inlines = [PickupItemInline]
    readonly_fields = ['pickup_number', 'confirmed_by', 'confirmed_at']
