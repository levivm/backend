import re
import time as time_a

from html import unescape
from datetime import time, date, datetime
from rest_framework import serializers
from rest_framework.fields import ImageField
from django.utils.html import escape


class AmazonS3FileField(ImageField):

    def __init__(self, base_path=None, *args, **kwargs):
        self._base_path = base_path
        super(AmazonS3FileField, self).__init__(**kwargs)

    def to_representation(self, file):
        """ Return correct URL Encode S3 path from a file"""
        if not file:
            return

        # file_name = quote(unicodedata.normalize('NFD', file.name).encode('utf-8'))
        return file.url



class BankField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(BankField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return dict(self._choices).get(obj)

    def to_internal_value(self, data):
        return data


class UnixEpochDateField(serializers.DateTimeField):

    def to_representation(self, value):

        """ Return epoch time for a datetime object or ``None``"""

        if type(value) is time:
            d = date.today()
            value = datetime.combine(d, value)

        try:
            return time_a.mktime(value.timetuple()) * 1000
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        return datetime.fromtimestamp(value // 1000).replace(second=0)


class HTMLField(serializers.CharField):

    def to_representation(self, value):
        """ Return HTML code escaped """

        return unescape(value)

    def to_internal_value(self, value):
        """ Return HTML code from escaped HTML value """
        # remove trailing p tags
        PAGRAPH_PATTERN = r'(<p><br/></p>)+$'
        clean_value = re.sub(PAGRAPH_PATTERN, '', value)
        return escape(clean_value)


class RemovableSerializerFieldMixin(object):

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        super(RemovableSerializerFieldMixin, self).__init__(*args, **kwargs)

        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)
