from django import forms
from .models import Organizer




#class OrganizerSignUpForm(forms.ModelForm):



class OrganizerForm(forms.ModelForm):
    name = forms.CharField()
    photo = forms.CharField(required=False)
    telephone = forms.CharField()
    youtube_video_url = forms.URLField(required=False)
    website   = forms.CharField(required=False)
    bio = forms.CharField(required=False)
    #location_id = forms.ModelChoiceField(widget=forms.HiddenInput(),
    #                                     queryset=City.objects.all())
    #location = forms.CharField(widget=forms.TextInput(attrs={
    #    'placeholder': _('Where the Streets have no name'), 'autocomplete': 'off'
    #}))

    class Meta:
        model = Organizer
        fields = ['name', 'photo', 'telephone', 'youtube_video_url','website','bio']