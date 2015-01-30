from activities.models import Activity,Category,SubCategory,Tags
from organizers.models import Organizer
from rest_framework import serializers
from django.core.urlresolvers import reverse
from locations.serializers import LocationsSerializer







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

        latitude  = data.get("location[point][latitude]")
        longitude = data.get("location[point][longitude]")
        city_id   = data.get("location[city][id]")
        address   = data.get("location[address]")
        print "CITTTTTTTTTTTTTTTTTTTTT",city_id
        location_data = {
            'city'  : city_id,
            'point' : [longitude,latitude],
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
        print "dataaaaaaaaaaaaaaaaaaaaaaaaaaa",request.DATA
        organizer = None
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError("Usuario no es organizador")

        data['organizer'] = organizer

        data['location']  = self._set_location(request.DATA)
        


        return data

    def create(self, validated_data):
        print "dataaaaaaaaaaaaaaaaaaaaaaaaaaa",validated_data
        request = self.context['request']
        _tags = request.DATA.getlist('tags[]')

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

        instance.title = validated_data.get('title', instance.title)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.large_description = validated_data.get('large_description', instance.large_description)
        instance.sub_category = validated_data.get('sub_category', instance.sub_category)
        instance.level = validated_data.get('level', instance.level)
        instance.type = validated_data.get('type', instance.type)
        instance.goals = validated_data.get('goals', instance.goals)
        instance.methodology = validated_data.get('methodology', instance.methodology)
        instance.content = validated_data.get('content', instance.content)
        instance.audience = validated_data.get('audience', instance.audience)
        instance.requirements = validated_data.get('requirements', instance.requirements)
        instance.return_policy = validated_data.get('return_policy', instance.return_policy)
        instance.extra_info = validated_data.get('extra_info', instance.extra_info)
        #instance.location = validated_data.get('location', instance.location)
        location = validated_data.get('location', None)
        if location:
            instance.location = location


        instance.save()

        _tags = request.DATA.getlist('tags[]')
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


