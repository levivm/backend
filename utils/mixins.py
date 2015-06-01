# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
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