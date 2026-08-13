from django.db import models

from .wol import normalize_mac


class Device(models.Model):
    name = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField(
        blank=True, null=True,
        help_text="Optional. The device's normal IP address, just for reference."
    )
    broadcast_address = models.GenericIPAddressField(
        default='255.255.255.255',
        help_text="Broadcast address to send the magic packet to, e.g. 255.255.255.255 "
                   "or a subnet broadcast like 192.168.1.255."
    )
    port = models.PositiveIntegerField(default=9, help_text="UDP port (7 or 9 are conventional).")
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_woken_at = models.DateTimeField(blank=True, null=True)
    wake_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.mac_address})'

    def save(self, *args, **kwargs):
        # Always store the MAC address in a normalized, consistent format.
        self.mac_address = normalize_mac(self.mac_address)
        super().save(*args, **kwargs)
