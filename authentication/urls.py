from django.conf.urls import url

from authentication.views import LoginView, SignUpStudentView, SignUpOrganizerView

urlpatterns = [
    # auth:login - api/auth/login
    url(
        regex=r'^login/?$',
        view=LoginView.as_view(),
        name='login'
    ),

    # auth:signup_student - api/auth/signup
    url(
        regex=r'^signup/?$',
        view=SignUpStudentView.as_view(),
        name='signup_student'
    ),

    # auth:signup_organizer - api/auth/signup/<token>
    url(
        regex=r'^signup/(?P<token>\w+)/?$',
        view=SignUpOrganizerView.as_view(),
        name='signup_organizer'
    ),
]