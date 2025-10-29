# apps/common/models.py
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with common timestamps.

    Fields:
      - created_at: set on insert
      - updated_at: set on each save
      - deleted_at: nullable soft-delete marker (not enforced)
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Deleted at")

    class Meta:
        abstract = True

    # --- handy soft-delete helpers (no schema impact) ---
    def mark_deleted(self) -> None:
        """Soft-delete: set deleted_at to now."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self) -> None:
        """Undo soft-delete: clear deleted_at."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])
