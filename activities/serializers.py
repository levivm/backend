# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"

from activities.models import Activity,Category,SubCategory,Tags,Chronogram,Session
from organizers.models import Organizer
from rest_framework import serializers
from django.core.urlresolvers import reverse
from locations.serializers import LocationsSerializer
from django.utils.translation import ugettext_lazy as _
from datetime import datetime,time,date
from calendar import  timegm




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



class ActivitiesSerializer(serializers.ModelSerializer):

    tags = serializers.SlugRelatedField(many=True,slug_field='name',read_only=True)
    #sub_category = SubCategoriesSerializer(required=True)
    #sub_category = SubCategoriesSerializer(required=True)
    sub_category  = serializers.SlugRelatedField(slug_field='id',queryset=SubCategory.objects.all(),required=True)
    category = serializers.CharField(write_only=True,required=True)
    category_id = serializers.SlugRelatedField(source='sub_category.category',read_only=True,slug_field='id') 
    location =  LocationsSerializer(read_only=True)
   

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
            )
        depth = 1





    def _set_location(self,data):

        location = data.get('location')

        city    = location["city"]
        if isinstance(city,dict):
            city = city["id"]

        #city = _city["id"] if 'id' in _city else _city

        point   = location["point"]
        address = location["address"]


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

        if request.method == "PUT":
            #ocation_data = 
            data['location']  = self._set_location(request.DATA)
            #print "LOOOOCC",data['location']
        


        return data

    def create(self, validated_data):
        print "dataaaaaaaaaaaaaaaaaaaaaaaaaaa",validated_data
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
        print "sssssssssssssssssssss",validated_data
        location = validated_data.get('location', None)
        del(validated_data['location'])
        instance.update(validated_data)
        # instance.title = validated_data.get('title', instance.title)
        # instance.short_description = validated_data.get('short_description', instance.short_description)
        # instance.large_description = validated_data.get('large_description', instance.large_description)
        # instance.sub_category = validated_data.get('sub_category', instance.sub_category)
        # instance.level = validated_data.get('level', instance.level)
        # instance.type = validated_data.get('type', instance.type)
        # instance.goals = validated_data.get('goals', instance.goals)
        # instance.methodology = validated_data.get('methodology', instance.methodology)
        # instance.content = validated_data.get('content', instance.content)
        # instance.audience = validated_data.get('audience', instance.audience)
        # instance.requirements = validated_data.get('requirements', instance.requirements)
        # instance.return_policy = validated_data.get('return_policy', instance.return_policy)
        # instance.extra_info = validated_data.get('extra_info', instance.extra_info)
        # instance.extra_info = validated_data.get('return_policy', instance.return_policy)
        #instance.location = validated_data.get('location', instance.location)
        if location:
            instance.location = location


        instance.save()

        _tags = request.DATA.get('tags')
        tags  = Tags.update_or_create(_tags)
        instance.tags.clear()
        instance.tags.add(*tags)

        

        # latitude = request.DATA.get("location['point'][latitude]")
        # longitude = request.DATA.get("location['point'][longitude]")
        # location_data = {
        #     'point' : [longitude,latitude]
        # }

        # location_serializer = LocationsSerializer(data=location_data)
        # if location_serializer.is_valid(raise_exception=True):
        #     l = location_serializer.save()
        #point = fromstr("POINT(%s %s)" % (location[1], location[2]))

        return instance






# class timestampField(serializers.Field):
#     """
#     Color objects are serialized into 'rgb(#, #, #)' notation.
#     """
#     def to_representation(self, obj):
#         #print "IBJJJ",obj
#         #return {'latitude':objk}obj
#         return obj

#     def to_internal_value(self, data):
#         #print "SAVING",data
#         #date = fromstr("POINT(%s %s)" % (data[1], data[0]))
#         date = datetime.utcfromtimestamp(float(data)/1000.0).date()
#         print "date",date
#         return date





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
    #activity =  serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all(),read_only=False)
    #activity           = serializers.SlugRelatedField(slug_field='id',read_only=False,queryset=Activity.objects.all())
    #initial_date = serializers.DateField()
    #date = timestampField(many=True)
    date       = UnixEpochDateField()
    start_time = UnixEpochDateField()
    end_time   = UnixEpochDateField()
    #closing_sale = serializers.DateField(input_formats=['%m/%d/%Y'])

    class Meta:
        model   = Session
        fields = ( 
            'id',
            'date',
            'start_time',
            'end_time',
            
            )


    def validate_start_time(self,value):
        #print "im validating start tim",value
        return value

    def validate(self,data):
        #start_time = 
        #print data
        print "DATEEEEE",data["date"]
        start_time = data['start_time']
        end_time   = data['end_time']
        #print "VALIDATE IN SESSION",data
        #print "VALIDATE IN SESSION",self.context['request']

        if start_time>=end_time:
            raise serializers.ValidationError(_("La hora de inicio debe ser mayor a la hora de inicio"))
        return data




class ChronogramsSerializer(serializers.ModelSerializer): 
    #activity =  serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all(),read_only=False)
    #activity           = serializers.SlugRelatedField(slug_field='id',read_only=False,queryset=Activity.objects.all())
    #initial_date = serializers.DateField()
    sessions = SessionsSerializer(many=True)

    #sessions = serializers.SerializerMethodField()
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

    # def validate_closing_sale(self,value):
    #     print "DTT",dt
    #     timestamp = value
    #     dt = datetime.utcfromtimestamp(timestamp)
    #     return dt

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
        #print "1111111111111111111111111",data
        #request = self.context['request']

        initial_date = data['initial_date']
        closing_sale = data['closing_sale']
        if initial_date > closing_sale:
            raise serializers.ValidationError(_("La fecha de cierre debe ser mayor a la fecha de inicio."))


        #print "sessions",data['sessions']
        #print "1111111111111111111111",data
        #sessions = data['sessions']
        self._valid_sessions(data)
        
        #_sessions = data['sessions']
        #is_sorted = all(_sessions[i]['date'] <= _sessions[i+1]['date']\
        #                             for i in xrange(len(_sessions)-1))
        #print "IS SORTEDDDDDDD",is_sorted
        #print "IS SORTEDDDDDDD",is_sorted
        #print "IS SORTEDDDDDDD",is_sorted
        #print "IS SORTEDDDDDDD",is_sorted
        # sessions  = []
        #for session in _sessions:
        #    print "dates" , session.date    
        #     if session_s.is_valid(raise_exception=True):
        #         sessions.append(session)

        return data


    def create(self, validated_data):
        #print "dataaaaaaaaaaaaaaaaaaaaaaaaaaa",validated_data


        sessions_data = validated_data.get('sessions')
        del(validated_data['sessions'])
        chronogram = Chronogram.objects.create(**validated_data)
        #print "chrongoram",chronogram
        #print "SESSION_DATA",sessions_data[0]
        _sessions = [Session(chronogram=chronogram,**data) for data in sessions_data]
        print "sessions",_sessions[0].__dict__
        sessions = Session.objects.bulk_create(_sessions)


        #validated_data['sessions'] = sessions
        #activity.tags.clear()
        #activity.tags.add(*tags)
        #print chronogram,"chro"
        return chronogram

    def update(self, instance, validated_data):
        sessions_data = validated_data.get('sessions')
        del(validated_data['sessions'])
        instance.update(validated_data)
        sessions = instance.sessions.all()
        sessions.delete()

        _sessions = [Session(chronogram=instance,**data) for data in sessions_data]
        #print "sessions",_sessions[0].__dict__
        sessions = Session.objects.bulk_create(_sessions)

        #print "sessions que me quedan",instance.sessions.all()

        return instance



        
    #     #return data
    #     #d1 = datetime.strptime(d1, "%Y-%m-%d")
    #     #d2 = datetime.strptime(d2, "%Y-%m-%d")

    # def create(self, validated_data):
    #     print "create Chronogram serializer"
    #     request = self.context['request']
    #     print request.DATA
    #     return Chronogram.objects.create(**validated_data)
    # def update(self, instance, validated_data):
    #     instance.initial_date = validated_data.get('initial_date', instance.initial_date)
    #     instance.closing_sale = validated_data.get('closing_sale', instance.closing_sale)
    #     instance.price        = validated_data.get('price', instance.price)
    #     instance.save()

