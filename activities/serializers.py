# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"

from activities.models import Activity,Category,SubCategory,Tags,Chronogram,Session,ActivityPhoto
from organizers.models import Organizer,Instructor
from organizers.serializers import InstructorsSerializer
from rest_framework import serializers
from django.core.urlresolvers import reverse
from locations.serializers import LocationsSerializer
from django.utils.translation import ugettext_lazy as _
from datetime import datetime,time,date
from calendar import  timegm
from django.conf import settings




class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = (
            'name',
            )



class SubCategoriesSerializer(serializers.ModelSerializer):


    category = serializers.SlugRelatedField(
        queryset = Category.objects.all(),
        slug_field='id',
     )

    class Meta:
        model = SubCategory
        fields = (
            'name',
            'id',
            'category'
            )
        depth = 1




class CategoriesSerializer(serializers.ModelSerializer):

    subcategories = SubCategoriesSerializer(many=True, read_only=True,source='subcategory_set')


    class Meta:
        model = Category
        fields = (
            'name',
            'id',
            'subcategories'
            )


class ActivityPhotosSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityPhoto
        fields = (
            'photo',
            'id'
            )




class UnixEpochDateField(serializers.DateTimeField):


    def to_representation(self, value):

        """ Return epoch time for a datetime object or ``None``"""
        #return int(time.mktime(value.timetuple()))
        
        if type(value) is time:
            d = date.today()
            value = datetime.combine(d,value)

        try:
            return timegm(value.timetuple())*1000
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        return datetime.utcfromtimestamp(float(value)/1000).replace(second=0)


class SessionsSerializer(serializers.ModelSerializer): 
    date       = UnixEpochDateField()
    start_time = UnixEpochDateField()
    end_time   = UnixEpochDateField()

    class Meta:
        model   = Session
        fields = ( 
            'id',
            'date',
            'start_time',
            'end_time',
            
            )



    def validate(self,data):

        start_time = data['start_time']
        end_time   = data['end_time']

        if start_time>=end_time:
            raise serializers.ValidationError(_("La hora de inicio debe ser menor a la hora final"))
        return data




class ChronogramsSerializer(serializers.ModelSerializer): 
    sessions = SessionsSerializer(many=True)
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())
    initial_date = UnixEpochDateField()
    closing_sale = UnixEpochDateField()
    
    class Meta:
        model   = Chronogram
        fields = ( 
            'id',
            'activity',
            'initial_date',
            'closing_sale',
            'number_of_sessions',
            'session_price',
            'capacity',
            'sessions',
            )
        depth = 1



    def validate_activity(self,value):
        #print "VALIDATINGGGACITIVITIIiyiy",value
        return value

    def validate_schedules(self,value):
        #print "values",value
        return value

    def validate_initial_date(self,value):
        #print "AQUIUU",value
        return value

    def validate_sessions(self,value):
        #print "validaingggggggg sess",value
        return value

    def validate_session_price(self,value):
        #print "validaint session_price",value
        if value<1: 
            raise serializers.ValidationError(_("El precio no puede ser negativo."))
        return value

    def validate_capacity(self,value):
        if value<1: 
            raise serializers.ValidationError(_("La capacidad no puede ser negativa."))
        return value

    def validate_number_of_sessions(self,value):
        if value<1:
            raise serializers.ValidationError(_(u"Debe especificar por lo menos una sesión"))            
        return value


    def _valid_sessions(self,data):
        
        session_data = data['sessions']
        initial_date = data['initial_date']

        f_range = len(session_data)
        for i in xrange(f_range):

            session    = session_data[i]
            n_session  = session_data[i+1] if i+1 < f_range else None 

            date   = session['date'].date()
            
            if date < initial_date.date():
                msg = u'La sesión no puede empezar antes de la fecha de inicio'
                raise serializers.ValidationError({'sessions_'+str(i):_(msg)}) 

            if not n_session:
                continue

            n_date = n_session['date'].date()

            if date > n_date:
                msg = u'La fecha su sesión debe ser mayor a la anterior'
                raise serializers.ValidationError({'sessions_'+str(i+1):_(msg)}) 
            elif date == n_date:

                if session['end_time'].time()>n_session['start_time'].time():
                    msg = u'La hora de inicio de su sesión debe ser después de la sesión anterior'
                    raise serializers.ValidationError({'sessions_'+str(i+1):_(msg)})

    def validate(self, data):

        initial_date = data['initial_date']
        closing_sale = data['closing_sale']
        if initial_date > closing_sale:
            raise serializers.ValidationError(_("La fecha de cierre debe ser mayor a la fecha de inicio."))

        self._valid_sessions(data)
        
        return data


    def create(self, validated_data):
        sessions_data = validated_data.get('sessions')
        del(validated_data['sessions'])
        chronogram = Chronogram.objects.create(**validated_data)
        _sessions = [Session(chronogram=chronogram,**data) for data in sessions_data]
        sessions = Session.objects.bulk_create(_sessions)

        return chronogram

    def update(self, instance, validated_data):


        sessions_data = validated_data.get('sessions')
        del(validated_data['sessions'])
        instance.update(validated_data)
        sessions = instance.sessions.all()
        sessions.delete()

        _sessions = [Session(chronogram=instance,**data) for data in sessions_data]
        sessions = Session.objects.bulk_create(_sessions)


        return instance






class ActivitiesSerializer(serializers.ModelSerializer):

    tags = serializers.SlugRelatedField(many=True,slug_field='name',read_only=True)
    sub_category  = serializers.SlugRelatedField(slug_field='id',queryset=SubCategory.objects.all(),required=True)
    category = serializers.CharField(write_only=True,required=True)
    category_id = serializers.SlugRelatedField(source='sub_category.category',read_only=True,slug_field='id') 
    location =  LocationsSerializer(read_only=True)
    photos   = ActivityPhotosSerializer(read_only=True,many=True)
    completed_steps = serializers.SerializerMethodField(read_only=True)
    chronograms = ChronogramsSerializer(read_only=True,many=True)
    last_date = serializers.SerializerMethodField()
    instructors = InstructorsSerializer(many=True,required=False)

    



    class Meta:
        model = Activity
        fields = (
            'id',
            'type',
            'title',
            'short_description',
            'large_description',
            'sub_category',
            'level',
            'tags',
            'category',
            'category_id',
            'content',
            'requirements',
            'return_policy',
            'extra_info',
            'audience',
            'goals',
            'methodology',
            'location',
            'photos',
            'youtube_video_url',
            'completed_steps',
            'published',
            'enroll_open',
            'last_date',
            'chronograms',
            'instructors',

            )
        depth = 1


    def get_completed_steps(self,obj):

        steps_requirements = settings.STEPS_REQUIREMENTS
        steps = steps_requirements.keys()
        completed_steps = {}
        related_fields  = [rel.get_accessor_name() for rel in obj._meta.get_all_related_objects()]
        related_fields += [rel.name for rel in obj._meta.many_to_many]
        for step in steps:
            required_attrs = steps_requirements[step]
            completed = True
            for attr in required_attrs:

                if attr in related_fields:
                    if not getattr(obj,attr,None).all():
                        completed = False
                        break
                else:
                    if not  getattr(obj,attr,None):
                        completed = False
                        break

            completed_steps[step] = completed
        return completed_steps
                


    def get_last_date(self,obj):
        return UnixEpochDateField().to_representation(obj.last_sale_date())



        



    def _set_location(self,location):


        city    = location["city"]
        if isinstance(city,dict):
            city = city["id"]


        point   = location["point"]
        address = location.get("address","")


        location_data = {
            'city'  : city,
            'point' : [point[1],point[0]],
            'address': address

        }

        location_serializer = LocationsSerializer(data=location_data)
        value = None
        if location_serializer.is_valid(raise_exception=True):
            value = location_serializer.save()

        return value

    def validate(self, data):
        request = self.context['request']
        user    = request.user
        organizer = None
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError("Usuario no es organizador")



        data['organizer'] = organizer

        location_data = request.data.get('location',None)
        data['location'] = self._set_location(location_data) if location_data else None 
        
        return data

    def create(self, validated_data):
        request = self.context['request']
        _tags = request.DATA.get('tags')

        tags  = Tags.update_or_create(_tags)
        if 'category' in validated_data:
            del validated_data['category']
        activity = Activity.objects.create(**validated_data)
        activity.tags.clear()
        activity.tags.add(*tags)
        return activity

    def update(self, instance, validated_data):

        request = self.context['request']
        organizer = validated_data.get('organizer')
        instructor_data = validated_data.get('instructors', [])

        instance.add_instructors(instructor_data,organizer)



        location = validated_data.get('location', None)
        del(validated_data['location'])
        instance.update(validated_data)

        if location:
            instance.location = location


        instance.save()

        _tags = request.DATA.get('tags')
        tags  = Tags.update_or_create(_tags)
        instance.tags.clear()
        instance.tags.add(*tags)


        return instance



