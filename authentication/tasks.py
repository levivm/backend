from django.contrib.auth.models import User

from authentication.models import ResetPasswordToken, ConfirmEmailToken
from utils.tasks import SendEmailTaskMixin


class ChangePasswordNoticeTask(SendEmailTaskMixin):
    """
    Task to send notification when the password has changed
    """

    def run(self, user_id, *args, **kwargs):
        self.user = User.objects.get(id=user_id)
        self.template_name = 'authentication/email/password_has_changed.html'
        self.emails = [self.user.email]
        self.subject = 'Tu contraseña ha cambiado'
        self.global_context = {}
        return super(ChangePasswordNoticeTask, self).run(*args, **kwargs)


class SendEmailResetPasswordTask(SendEmailTaskMixin):
    """
    Task to send the link to reset the password
    """

    def run(self, reset_password_id, *args, **kwargs):
        self.reset_password = ResetPasswordToken.objects.get(id=reset_password_id)
        self.template_name = 'authentication/email/reset_password.html'
        self.emails = [self.reset_password.user.email]
        self.subject = 'Reinicio de contraseña'
        self.global_context = self.get_context_data()
        return super(SendEmailResetPasswordTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'url': self.reset_password.get_token_url()
        }


class SendEmailConfirmEmailTask(SendEmailTaskMixin):
    """
    Task to send the confirmation email
    """

    def run(self, confirm_email_id, *args, **kwargs):
        self.confirm_email = ConfirmEmailToken.objects.get(id=confirm_email_id)
        self.template_name = 'authentication/email/confirm_email.html'
        self.emails = [self.confirm_email.email]
        self.subject = 'Confirmación de correo'
        self.global_context = self.get_context_data()
        return super(SendEmailConfirmEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'name': self.confirm_email.user.first_name,
            'url': self.confirm_email.get_token_url(),
        }