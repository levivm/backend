import datetime

from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now


class GeneralMetricsMixin(object):

    def __init__(self):
            super(GeneralMetricsMixin, self).__init__()
            self.marketing = Group.objects.get(name='Marketing')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and (request.user.is_superuser or (
                    request.user.is_staff and self.marketing in request.user.groups.all())):
            return super(GeneralMetricsMixin, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied

    def set_dates(self, start, end):
        self.start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date() if \
            start else now().date() - relativedelta(months=1)
        self.end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date() if \
            end else now().date()
