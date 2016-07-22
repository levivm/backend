from django.http.response import HttpResponse
from django.views.generic.base import TemplateView, View

from metrics.metrics import GeneralMetrics
from metrics.mixins import GeneralMetricsMixin
from metrics.tasks import SendEmailGeneralMetricsExportTask


class GeneralMetricsTemplateView(GeneralMetricsMixin, TemplateView):
    template_name = 'metrics/general_metrics.html'

    def get(self, request, *args, **kwargs):
        self.set_dates(start=request.GET.get('start_date'), end=request.GET.get('end_date'))
        self.general_metrics = GeneralMetrics(start_date=self.start_date, end_date=self.end_date)
        self.general_metrics.range_metrics = self.general_metrics.get_range_metrics()
        self.general_metrics.total_metrics = self.general_metrics.get_total_metrics()
        return super(GeneralMetricsTemplateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GeneralMetricsTemplateView, self).get_context_data(**kwargs)
        context['start_date'] = self.start_date
        context['end_date'] = self.end_date
        context['general_metrics'] = self.general_metrics
        return context


class GeneralMetricsExportView(GeneralMetricsMixin, View):

    def get(self, request, *args, **kwargs):
        self.set_dates(start=request.GET.get('start_date'), end=request.GET.get('end_date'))
        task = SendEmailGeneralMetricsExportTask()
        task.delay(email=request.user.email, start_date=self.start_date, end_date=self.end_date,
                   category=request.GET['type'])
        return HttpResponse('OK')
