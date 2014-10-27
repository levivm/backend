from django.conf.urls import patterns, include, url

#from users import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'users.views.index'),
    # url(r'^blog/', include('blog.urls')),

)
