from django.contrib.postgres.fields import JSONField
from django.db import models


class CeleryTaskEditActivity(models.Model):
    task_id = models.CharField(max_length=40)
    date = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=30)

    class Meta:
        abstract = True


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
