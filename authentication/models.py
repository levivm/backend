import hashlib

import os

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class AuthVerifyToken(models.Model):
    token = models.CharField(max_length=40, unique=True, blank=True)
    valid_until = models.DateTimeField(blank=True)
    used = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = self.generate_token()

        if not self.valid_until:
            self.valid_until = now() + timedelta(weeks=1)

        super(AuthVerifyToken, self).save(*args, **kwargs)

    def generate_token(self):
        while True:
            token = hashlib.sha1(os.urandom(128)).hexdigest()
            if not self._meta.model.objects.filter(token=token).exists():
                return token


class ResetPasswordToken(AuthVerifyToken):

    def get_token_url(self):
        return '%spassword/restablecer/key/%s' % (settings.FRONT_SERVER_URL, self.token)


class ConfirmEmailToken(AuthVerifyToken):
    email = models.EmailField()

    def get_token_url(self):
        return '%semail/confirmar/%s' % (settings.FRONT_SERVER_URL, self.token)
