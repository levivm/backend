# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class FileUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        content = self.cleaned_data['file']
        content_type = content.content_type.split('/')[0]
        if content_type in settings.CONTENT_TYPES:
            if content._size > settings.MAX_UPLOAD_PHOTO_SIZE:
                msg = _('Mantenga el tamaño del archivo por debajo %s. Tamaño actual %s'\
                        % (filesizeformat(settings.MAX_UPLOAD_PHOTO_SIZE), filesizeformat(content._size)))
                raise forms.ValidationError(msg)
        else:
            raise forms.ValidationError(_('El tipo de archivo no es soportado'))
        return content