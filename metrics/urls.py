from django.conf.urls import url

from metrics.views import GeneralMetricsTemplateView

urlpatterns = [

    # metrics:general_metrics
    url(
        regex=r'^general/?$',
        view=GeneralMetricsTemplateView.as_view(),
        name='general',
    ),
]
