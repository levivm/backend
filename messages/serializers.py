from rest_framework import serializers

from django.utils.translation import ugettext as _

from messages.models import OrganizerMessage


class OrganizerMessageSerializer(serializers.ModelSerializer):
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = OrganizerMessage
        fields = (
            'id',
            'subject',
            'message',
            'created_at',
            'organizer',
        )

    def validate(self, data):
        organizer = self.context.get('organizer')

        if organizer is None:
            raise serializers.ValidationError({'organizer': _('El organizador es requerido.')})

        data['organizer'] = organizer
        return data

    def get_organizer(self, obj):
        try:
            obj.organizer.photo.file
        except ValueError:
            photo = None
        else:
            photo = obj.organizer.photo

        return {
            'id': obj.organizer.id,
            'name': obj.organizer.name,
            'photo': photo,
        }
