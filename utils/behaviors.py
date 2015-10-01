from random import sample
from string import ascii_uppercase

from django.db import models


class Tokenizable(models.Model):
    token = models.CharField(max_length=20, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            self.token = self.generate_token()

        super(Tokenizable, self).save(*args, **kwargs)

    def generate_token(self, size=5, chars=ascii_uppercase, prefix=None):
        while True:
            pretoken = ''.join(sample(chars, size))
            token = '%s-%s' % (prefix, pretoken) if prefix else pretoken

            if not self._meta.model.objects.filter(token=token).exists():
                return token


class Updateable(models.Model):


    class Meta:
        abstract = True


    def update(self,data):
        for (key, value) in data.items():
            setattr(self, key, value)
        self.save()
