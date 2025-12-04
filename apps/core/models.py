"""
Core utilities and base classes for the application.
Add shared models, mixins, utilities here.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields.
    Use this as a base for models that need timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
