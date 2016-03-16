from django.conf.urls import url

from authentication.views import LoginView, SignUpStudentView, SignUpOrganizerView, SocialAuthView, \
    ChangePasswordView, ForgotPasswordView, ResetPasswordView, ConfirmEmailView, ChangeEmailView, \
    VerifyConfirmEmailTokenView, VerifyResetPasswordTokenView, RequestSignupViewSet, \
    VerifySignupOrganizerToken

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

    # auth:social_login_signup - api/auth/login/<provider>
    url(
        regex=r'^login/(?P<provider>\w+)/?$',
        view=SocialAuthView.as_view(),
        name='social_login_signup',
    ),

    # auth:change_password - api/auth/password/change
    url(
        regex=r'^password/change/?$',
        view=ChangePasswordView.as_view(),
        name='change_password',
    ),

    # auth:forgot_password - api/auth/password/forgot
    url(
        regex=r'^password/forgot/?$',
        view=ForgotPasswordView.as_view(),
        name='forgot_password',
    ),

    # auth:reset_password - api/auth/password/reset
    url(
        regex=r'^password/reset/?$',
        view=ResetPasswordView.as_view(),
        name='reset_password',
    ),

    # auth:confirm_email - api/auth/email/confirm
    url(
        regex=r'^email/confirm/?$',
        view=ConfirmEmailView.as_view(),
        name='confirm_email',
    ),

    # auth:change_email - api/auth/email/change
    url(
        regex=r'^email/change/?$',
        view=ChangeEmailView.as_view(),
        name='change_email',
    ),

    # auth:verify_email_token - api/auth/email/verify
    url(
        regex=r'^email/verify/(?P<token>\w+)/?$',
        view=VerifyConfirmEmailTokenView.as_view(),
        name='verify_email_token',
    ),

    # auth:verify_password_token - api/auth/password/verify
    url(
        regex=r'^password/verify/(?P<token>\w+)/?$',
        view=VerifyResetPasswordTokenView.as_view(),
        name='verify_password_token',
    ),

    # auth:request_signup - api/auth/request/signup
    url(
        regex=r'^request/signup/?$',
        view=RequestSignupViewSet.as_view({'post':'create'}),
        name='request_signup',
    ),
    # auth:request_signup - api/auth/request/signup/token/<token>
    url(
        regex=r'^request/signup/token/(?P<key>\w+)/$',
        view=VerifySignupOrganizerToken.as_view(),
        name='request_signup_token',
    ),

]
