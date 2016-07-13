from django.conf.urls import url

from metrics.views import GeneralMetricsTemplateView, GeneralMetricsExportView

urlpatterns = [

    # metrics:general
    url(
        regex=r'^general/?$',
        view=GeneralMetricsTemplateView.as_view(),
        name='general',
    ),

    # metrics:export
    url(
        regex=r'^general/export/?$',
        view=GeneralMetricsExportView.as_view(),
        name='export',
    )
]
