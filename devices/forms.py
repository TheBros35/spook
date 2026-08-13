from django import forms

from .models import Device
from .wol import is_valid_mac, normalize_mac


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'mac_address', 'ip_address', 'broadcast_address', 'port', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. Office Desktop'
            }),
            'mac_address': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'AA:BB:CC:DD:EE:FF'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '192.168.1.50 (optional)'
            }),
            'broadcast_address': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Optional notes'
            }),
        }

    def clean_mac_address(self):
        mac = self.cleaned_data['mac_address']
        if not is_valid_mac(mac):
            raise forms.ValidationError(
                'Enter a valid MAC address, e.g. AA:BB:CC:DD:EE:FF'
            )
        return normalize_mac(mac)
