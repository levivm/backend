from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import JSONField


class CeleryTask(models.Model):
    task_id = models.CharField(max_length=40)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.task_id


class EmailTaskRecord(models.Model):
    STATUS = (
        ('sent', 'SENT'),
        ('queued', 'QUEUED'),
        ('scheduled', 'SCHEDULED'),
        ('rejected', 'REJECTED'),
        ('invalid', 'INVALID'),
        ('error', 'ERROR'),
    )

    to = models.EmailField()
    template_name = models.CharField(max_length=300)
    subject = models.CharField(max_length=150)
    data = JSONField()
    status = models.CharField(max_length=50, default='queued', choices=STATUS)
    reject_reason = models.CharField(blank=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=50)
    smtp_id = models.CharField(blank=True, max_length=50)
