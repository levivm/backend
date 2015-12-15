# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
import io

from PIL import Image
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm
from rest_framework import serializers


class AssignPermissionsMixin(object):
    permissions = tuple()

    def assign_permissions(self, user, instance):
        for permission in self.permissions:
            assign_perm(permission, user, instance)


class FileUploadMixin(object):


    def clean_file(self, file):
        content_type = file.content_type.split('/')[0]
        if content_type in settings.CONTENT_TYPES:
            if file._size > settings.MAX_UPLOAD_PHOTO_SIZE:
                msg = _('Mantenga el tamaño del archivo por debajo %s. Tamaño actual %s' \
                        % (filesizeformat(settings.MAX_UPLOAD_PHOTO_SIZE), filesizeformat(file._size)))
                raise serializers.ValidationError(msg)
        else:
            raise serializers.ValidationError(_('El tipo de archivo no es soportado'))

        return file


class ImageOptimizable(object):
    MAX_SIZE = 480
    MIN_SIZE = 120
    QUALITY = 90
    FORMAT = 'JPEG'

    def optimize(self, bytesio, width, height):
        image = Image.open(bytesio)
        image = self.crop_square(image, width, height)

        if width > self.MAX_SIZE and height > self.MAX_SIZE:
            image = self.resize(image, size=self.MAX_SIZE)
        elif width < self.MIN_SIZE and height < self.MIN_SIZE:
            image = self.resize(image, size=self.MIN_SIZE)

        return self.save_buffer(image)

    def crop_square(self, image, width, height):
        size = width if width < height else height
        center = {'width': width // 2, 'height': height // 2}
        left = center['width'] - (size // 2)
        right = center['width'] + (size // 2)
        top = center['height'] - (size // 2)
        bottom = center['height'] + (size // 2)
        box = (left, top, right, bottom)

        image = image.crop(box)
        return image

    def resize(self, image, size):
        image = image.resize((size, size), Image.ANTIALIAS)
        return image

    def save_buffer(self, image):
        image_file = io.BytesIO()
        image.save(image_file, self.FORMAT, quality=self.QUALITY)
        return image_file