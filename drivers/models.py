"""
Driver Registry models.
Manages driver information for arrivals and delivery pickups.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class VehicleType(models.TextChoices):
    TRUCK = 'truck', _('Truck / ট্রাক')
    PICKUP = 'pickup', _('Pickup / পিকআপ')
    VAN = 'van', _('Van / ভ্যান')
    LORRY = 'lorry', _('Lorry / লরি')
    TRAILER = 'trailer', _('Trailer / ট্রেইলার')
    THREE_WHEELER = 'three_wheeler', _('Three Wheeler / তিন চাকা')
    OTHER = 'other', _('Other / অন্যান্য')


class Driver(BaseModel):
    """Driver entity for handling arrivals and pickups."""

    name = models.CharField(max_length=200, verbose_name=_('Full Name'))
    name_bn = models.CharField(max_length=200, blank=True, default='', verbose_name=_('নাম'))
    phone = models.CharField(max_length=20, unique=True, verbose_name=_('Phone Number'))
    alt_phone = models.CharField(max_length=20, blank=True, default='', verbose_name=_('Alternative Phone'))
    nid_number = models.CharField(max_length=20, blank=True, default='', verbose_name=_('NID Number'))
    license_number = models.CharField(max_length=50, unique=True, verbose_name=_('License Number'))
    vehicle_type = models.CharField(
        max_length=20, choices=VehicleType.choices,
        default=VehicleType.TRUCK, verbose_name=_('Vehicle Type'),
    )
    vehicle_number = models.CharField(max_length=50, verbose_name=_('Vehicle Number'))
    address = models.TextField(blank=True, default='', verbose_name=_('Address'))
    photo = models.ImageField(upload_to='drivers/%Y/%m/', blank=True, null=True)
    is_available = models.BooleanField(default=True, db_index=True, verbose_name=_('Available'))
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']
        verbose_name = _('Driver')
        verbose_name_plural = _('Drivers')
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['license_number']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f'{self.name} — {self.vehicle_number}'

    @property
    def total_trips(self):
        from arrivals.models import Arrival
        from pickups.models import Pickup
        arrivals = Arrival.objects.filter(driver=self).count()
        pickups = Pickup.objects.filter(driver=self).count()
        return arrivals + pickups
