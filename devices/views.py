from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import DeviceForm
from .models import Device
from .wol import send_magic_packet


def device_list(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Saved device "{form.cleaned_data["name"]}".')
            return redirect('device_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = DeviceForm()

    devices = Device.objects.all()
    return render(request, 'devices/device_list.html', {
        'devices': devices,
        'form': form,
    })


@require_POST
def device_wake(request, pk):
    device = get_object_or_404(Device, pk=pk)
    try:
        send_magic_packet(device.mac_address, device.broadcast_address, device.port)
    except (ValueError, OSError) as exc:
        messages.error(request, f'Failed to send Wake-on-LAN packet to "{device.name}": {exc}')
    else:
        device.last_woken_at = timezone.now()
        device.wake_count += 1
        device.save(update_fields=['last_woken_at', 'wake_count'])
        messages.success(request, f'Wake-on-LAN packet sent to "{device.name}".')
    return redirect('device_list')


@require_POST
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    name = device.name
    device.delete()
    messages.success(request, f'Deleted device "{name}".')
    return redirect('device_list')
