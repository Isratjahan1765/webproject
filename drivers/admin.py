from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'license_number', 'vehicle_type', 'vehicle_number', 'is_available']
    list_filter = ['vehicle_type', 'is_available']
    search_fields = ['name', 'phone', 'license_number', 'vehicle_number']
    list_editable = ['is_available']
