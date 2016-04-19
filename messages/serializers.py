from rest_framework import serializers

from django.utils.translation import ugettext as _

from messages.models import OrganizerMessage, OrganizerMessageStudentRelation


class OrganizerMessageSerializer(serializers.ModelSerializer):
    organizer = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()
    initial_date = serializers.SerializerMethodField()

    class Meta:
        model = OrganizerMessage
        fields = (
            'id',
            'subject',
            'message',
            'created_at',
            'organizer',
            'calendar',
            'activity',
            'initial_date',
        )

    def validate(self, data):
        organizer = self.context.get('organizer')
        calendar = data['calendar']

        if organizer is None:
            raise serializers.ValidationError({'organizer': _('El organizador es requerido.')})

        if calendar.activity.organizer != organizer:
            raise serializers.ValidationError({'calendar': _('Este calendario no pertenece a '
                                                             'este organizador')})

        data['organizer'] = organizer
        return data

    def get_organizer(self, obj):
        try:
            photo = obj.organizer.photo.url
        except ValueError:
            photo = None

        return {
            'id': obj.organizer.id,
            'name': obj.organizer.name,
            'photo': photo,
        }

    def get_activity(self, obj):
        return obj.calendar.activity.title

    def get_initial_date(self, obj):
        return obj.calendar.initial_date.isoformat()[:-6] + 'Z'


class OrganizerMessageStudentRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizerMessageStudentRelation

