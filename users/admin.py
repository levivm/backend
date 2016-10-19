from django.contrib import admin

from organizers.models import Organizer
from utils.mixins import OperativeModelAdminMixin
from .models import RequestSignup, OrganizerConfirmation
from .tasks import SendEmailOrganizerConfirmationTask


class OrganizerConfirmationStatusListFilter(admin.SimpleListFilter):
    title = 'Existe organizador'
    parameter_name = 'organizer_exists'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Si'),
            ('false', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            organizerconfirmation_list = [obj.id for obj in queryset if Organizer.objects.filter(
                user__email=obj.requested_signup.email).exists()]
            return OrganizerConfirmation.objects.filter(id__in=organizerconfirmation_list)
        elif self.value() == 'false':
            organizerconfirmation_list = [obj.id for obj in queryset if not Organizer.objects.filter(
                user__email=obj.requested_signup.email).exists()]
            return OrganizerConfirmation.objects.filter(id__in=organizerconfirmation_list)


def send_verification_email(modeladmin, request, queryset):
    for signup in queryset:
        signup.approved = True
        signup.save()

send_verification_email.short_description = "Send organizer verification email"


@admin.register(RequestSignup)
class RequestSignupAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('email', 'name', 'approved')
    list_filter = ('approved',)
    actions = [send_verification_email]
    operative_readonly_fields = {'email', 'name', 'telephone', 'city', 'document', 'document_type'}


@admin.register(OrganizerConfirmation)
class OrganizerConfirmationAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'organizer', 'email', 'organizer_exists', 'used', 'created')
    list_filter = (OrganizerConfirmationStatusListFilter,)
    operative_readonly_fields = {'requested_signup', 'created', 'key', 'sent', 'used'}

    def organizer(self, obj):
        try:
            return Organizer.objects.get(user__email=obj.requested_signup.email)
        except Organizer.DoesNotExist:
            return '-'

    def email(self, obj):
        return obj.requested_signup.email

    def organizer_exists(self, obj):
        return Organizer.objects.filter(user__email=obj.requested_signup.email).exists()

    organizer_exists.boolean = True
