from django.contrib import admin

from .forms import DeviceForm
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceForm
    list_display = ('name', 'mac_address', 'ip_address', 'broadcast_address', 'port', 'last_woken_at', 'wake_count')
    search_fields = ('name', 'mac_address', 'ip_address')
