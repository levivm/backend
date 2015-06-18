from calendar import timegm
from datetime import time, date, datetime
from rest_framework import serializers


class UnixEpochDateField(serializers.DateTimeField):


    def to_representation(self, value):

        """ Return epoch time for a datetime object or ``None``"""
        #return int(time.mktime(value.timetuple()))

        if type(value) is time:
            d = date.today()
            value = datetime.combine(d,value)

        try:
            return timegm(value.timetuple())*1000
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        return datetime.fromtimestamp(value//1000).replace(second=0)