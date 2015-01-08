from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings




class UserCreateForm(forms.Form):

    USER_TYPES = (
        ('O', _('Organizador')),
        ('S', _('Estudiante')),
    )

    user_type = forms.ChoiceField(choices=USER_TYPES,
                                  required=True)

    first_name = forms.CharField(required=True)
    last_name  = forms.CharField(required=True)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.user_type  = self.cleaned_data['user_type']
        user.save()


class FileUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        content = self.cleaned_data['file']
        content_type = content.content_type.split('/')[0]
        if content_type in settings.CONTENT_TYPES:
            if content._size > settings.MAX_UPLOAD_PHOTO_SIZE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_PHOTO_SIZE), filesizeformat(content._size)))
        else:
            raise forms.ValidationError(_('File type is not supported'))
        return content

    #error_messages = {
    #    'duplicate_email': _('A user with that email already exists.'),
    #    'password_mismatch': _('The two password fields didn\'t match.'),
    #}


    #first_name = forms.CharField(label=_("First name"),
    #                            widget=forms.TextInput(attrs={'placeholder': 'First name',
    #                                                          'autocomplete':'off'}),
    #                            required=True)

    #last_name  = forms.CharField(label=_("Last name"),
    #                            widget=forms.TextInput(attrs={'placeholder': 'Last name',
    #                                                          'autocomplete':'off'}),
    #                            required=True)

