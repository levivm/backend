from rest_framework import serializers

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
            'organizer'
        )

    def validate(self, data):
        data['organizer'] = self.context['organizer']
        return data

    def get_organizer(self, obj):
        return {
            'id': obj.organizer.id,
            'name': obj.organizer.name,
            'photo': obj.organizer.photo,
        }
