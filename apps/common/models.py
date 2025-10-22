from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted at')

    class Meta:
        abstract = True
