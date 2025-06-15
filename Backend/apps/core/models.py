from django.db import models
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.save()

    def restore(self):
        """Restore soft deleted object"""
        self.is_active = True
        self.save()


class TimestampedModel(models.Model):
    """
    Abstract model that provides timestamp fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True