import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.template.defaulttags import now
from django.utils.timezone import now
from django.views.generic.base import TemplateView

from metrics.metrics import GeneralMetrics


class GeneralMetricsTemplateView(TemplateView):
    template_name = 'metrics/general_metrics.html'

    def __init__(self):
        super(GeneralMetricsTemplateView, self).__init__()
        self.marketing = Group.objects.get(name='Marketing')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and (request.user.is_superuser or (
                    request.user.is_staff and self.marketing in request.user.groups.all())):
            return super(GeneralMetricsTemplateView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied

    def get(self, request, *args, **kwargs):
        self.set_dates(start=request.GET.get('start_date'), end=request.GET.get('end_date'))
        self.general_metrics = GeneralMetrics(start_date=self.start_date, end_date=self.end_date)
        return super(GeneralMetricsTemplateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GeneralMetricsTemplateView, self).get_context_data(**kwargs)
        context['start_date'] = self.start_date
        context['end_date'] = self.end_date
        context['general_metrics'] = self.general_metrics
        return context

    def set_dates(self, start, end):
        self.start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date() if \
            start else now().date() - relativedelta(months=1)
        self.end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date() if \
            end else now().date()
