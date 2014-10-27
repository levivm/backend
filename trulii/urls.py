from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trulii.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	(r'^users/logout/$', 'django.contrib.auth.views.logout',
     	{'next_page': '/'}),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('users.urls')),
    url(r'^users/', include('allauth.urls')),

)
