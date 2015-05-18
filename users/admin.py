from django.contrib import admin

from .models import RequestSignup,OrganizerConfirmation



def send_verification_email(modeladmin,request,queryset):
    for signup in queryset:
        signup.approved=True
        signup.save()

send_verification_email.short_description = "Send organizer verification email"


    

class RequestSignupAdmin(admin.ModelAdmin):
    list_display = ['email', 'name','telephone','want_to_teach','city','approved']
    actions = [send_verification_email]

admin.site.register(RequestSignup,RequestSignupAdmin)
admin.site.register(OrganizerConfirmation)
