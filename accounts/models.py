"""Accounts models — Profile management."""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class UserRole(models.TextChoices):
    MANAGER = 'manager', _('Warehouse Manager')
    OPERATOR = 'operator', _('Warehouse Operator')
    VIEWER = 'viewer', _('Viewer (Read Only)')


class Profile(TimeStampedModel):
    """Extended user profile."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=20, choices=UserRole.choices,
        default=UserRole.OPERATOR, verbose_name=_('Role'),
    )
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name=_('Phone'))
    designation = models.CharField(max_length=100, blank=True, default='', verbose_name=_('Designation'))
    avatar = models.ImageField(upload_to='avatars/%Y/', blank=True, null=True)
    language_preference = models.CharField(
        max_length=5, choices=settings.LANGUAGES,
        default='en', verbose_name=_('Language'),
    )
    receive_notifications = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.get_role_display()})'

    @property
    def is_manager(self):
        return self.role == UserRole.MANAGER

    @property
    def can_edit_products(self):
        return self.role == UserRole.MANAGER

    @property
    def can_confirm_arrivals(self):
        return self.role in [UserRole.MANAGER, UserRole.OPERATOR]
