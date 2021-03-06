import io
from itertools import filterfalse

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm
from rest_framework import serializers


class AssignPermissionsMixin(object):
    permissions = tuple()
    user = None
    obj = None
    kwargs = dict()

    def assign_permissions(self):
        for permission in self.permissions:
            assign_perm(permission, self.user, self.obj)

    def save(self, *args, **kwargs):
        self.kwargs = kwargs
        self.get_objs()

        create = False
        if not self.pk:
            create = True

        super(AssignPermissionsMixin, self).save(*args, **kwargs)

        if create:
            self.assign_permissions()

    def get_objs(self):
        self.user = self.kwargs.pop('user', None)
        self.obj = self.kwargs.pop('obj', None)
        assert self.user, 'Se necesita el parámetro user para poder asignar los permisos'
        assert self.obj, 'Se necesita el parámetro obj para poder asignar los permisos'


class FileUploadMixin(object):
    def clean_file(self, file):
        content_type = file.content_type.split('/')[0]
        if content_type in settings.CONTENT_TYPES:
            if file._size > settings.MAX_UPLOAD_PHOTO_SIZE:
                msg = _('Mantenga el tamaño del archivo por debajo %s. Tamaño actual %s' \
                        % (filesizeformat(settings.MAX_UPLOAD_PHOTO_SIZE),
                           filesizeformat(file._size)))
                raise serializers.ValidationError(msg)
        else:
            raise serializers.ValidationError(_('El tipo de archivo no es soportado'))

        return file


class ImageOptimizable(object):
    MAX_SIZE = 480
    MIN_SIZE = 120
    QUALITY = 90
    FORMAT = 'JPEG'

    def open(self, bytesio):
        return Image.open(bytesio)

    def create_thumbnail(self, bytesio, filename, width, height):
        image = self.open(bytesio)
        size = (width, height)
        image.thumbnail(size, Image.ANTIALIAS)

        buffer = self.save_buffer(image)
        buffer.seek(0)

        return SimpleUploadedFile(filename, buffer.read(), content_type='image/jpeg')

    def optimize(self, bytesio, width, height):
        image = self.open(bytesio)
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


class ListUniqueOrderedElementsMixin(object):
    @staticmethod
    def unique_everseen(iterable, key=None):
        "List unique elements, preserving order. Remember all elements ever seen."
        # unique_everseen('AAAABBBCCDAABBB') --> A B C D
        # unique_everseen('ABBCcAD', str.lower) --> A B C D
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in filterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element


class OperativeModelAdminMixin(object):
    readonly_fields = ()
    operative_readonly_fields = set()

    def __init__(self, *args, **kwargs):
        super(OperativeModelAdminMixin, self).__init__(*args, **kwargs)
        try:
            operative_group, _created = Group.objects.get_or_create(name='Operatives')
            self.operatives = operative_group.user_set.all()
        except:
            self.operatives = []

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = tuple()
        if request.user in self.operatives and obj:
            readonly_fields = tuple(set(self.readonly_fields) | self.operative_readonly_fields)
        return self.readonly_fields + readonly_fields
