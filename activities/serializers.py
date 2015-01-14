from activities.models import Activity,Category,SubCategory,Tags
from organizers.models import Organizer
from rest_framework import serializers
from django.core.urlresolvers import reverse







class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = (
            'name',
            )


class ActivitiesSerializer(serializers.ModelSerializer):

    tags = serializers.SlugRelatedField(many=True,slug_field='name',read_only=True)

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
            )



    def validate(self, data):
        #print "DATAAAAAAAAAAAa",self.context['request'].DATA.getlist('tags[]')
        #print "DATAAAAAAAAAAAa",self.context['request'].POST
        #print "DATAAAAAAAAAAAa",self.context['request'].POST.getlist('tags[]')
        print "validate",data
        request = self.context['request']
        user    = request.user
        organizer = None
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError("Usuario no es organizador")

        data['organizer'] = organizer
        return data

    def create(self, validated_data):
        request = self.context['request']
        print request.POST
        print request.DATA
        _tags = request.DATA.getlist('tags[]')

        tags  = Tags.update_or_create(_tags)
        activity = Activity.objects.create(**validated_data)
        activity.tags.clear()
        activity.tags.add(*tags)
        return activity

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

