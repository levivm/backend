from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from allauth.socialaccount.fields import JSONField


class CeleryTask(models.Model):
    task_id = models.CharField(max_length=40)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.task_id


class EmailTaskRecord(models.Model):
	data = JSONField()
	to   = models.EmailField()
	template = models.CharField(max_length=300)
	send = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)
	task_id = models.CharField(max_length=40)
