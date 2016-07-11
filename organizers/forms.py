from django import forms
from .models import Organizer


class OrganizerForm(forms.ModelForm):
    name = forms.CharField()
    photo = forms.CharField(required=False)
    telephone = forms.CharField()
    youtube_video_url = forms.URLField(required=False)
    website   = forms.CharField(required=False)
    bio = forms.CharField(required=False)


    class Meta:
        model = Organizer
        fields = ['name', 'photo', 'telephone', 'youtube_video_url','website','bio']