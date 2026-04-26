"""
Core abstract models used across all SPHWMS apps.
Provides soft-delete, timestamps, and audit trail base classes.
"""

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Custom manager that filters out soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_only(self):
        return super().get_queryset().filter(is_deleted=True)


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete capability."""
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark record as deleted instead of actually removing it."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Combined base model with timestamps and soft delete.
    All SPHWMS models should inherit from this.
    """

    class Meta:
        abstract = True
        ordering = ['-created_at']
