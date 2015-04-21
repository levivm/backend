from django.contrib import admin

from .models import RequestSignup,OrganizerConfirmation



def send_verification_email(modeladmin,request,queryset):
	for signup in queryset:
		signup.organizerconfirmation.send()

send_verification_email.short_description = "Send organizer verification email"

def accept_signup_request(modeladmin,request,queryset):
	queryset.update(approved=True)
	
accept_signup_request.short_description = "Accept organizer request signup"

class RequestSignupAdmin(admin.ModelAdmin):
	list_display = ['email', 'name','telephone','want_to_teach','city','approved']
	actions = [accept_signup_request,send_verification_email]

admin.site.register(RequestSignup,RequestSignupAdmin)
admin.site.register(OrganizerConfirmation)
