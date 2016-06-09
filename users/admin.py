from django.contrib import admin

from utils.mixins import OperativeModelAdminMixin
from .models import RequestSignup, OrganizerConfirmation
from .tasks import SendEmailOrganizerConfirmationTask


def send_verification_email(modeladmin, request, queryset):
    for signup in queryset:
        signup.approved = True
        signup.save()
        organizer_confirmation = signup.organizerconfirmation
        data = {
            'confirmation_id': organizer_confirmation.id
        }
        task = SendEmailOrganizerConfirmationTask()
        task.apply_async((organizer_confirmation.id,), data, countdown=2)


send_verification_email.short_description = "Send organizer verification email"


@admin.register(RequestSignup)
class RequestSignupAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ['email', 'name', 'telephone', 'document_type', 'document', 'city', 'approved']
    actions = [send_verification_email]
    operative_readonly_fields = {'email', 'name', 'telephone', 'city', 'document', 'document_type'}


@admin.register(OrganizerConfirmation)
class OrganizerConfirmationAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'requested_signup', 'created', 'key', 'sent', 'used'}
