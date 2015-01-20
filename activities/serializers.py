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
            'category_id'
            )

    def validate(self, data):
        request = self.context['request']
        user    = request.user
        print "dataaaaaaaaaaaaaaaaaaaaaaaaaaa",data
        organizer = None
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError("Usuario no es organizador")

        data['organizer'] = organizer
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


        instance.type = validated_data.get('username', instance.type)
        instance.title = validated_data.get('title', instance.title)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.large_description = validated_data.get('large_description', instance.large_description)
        instance.sub_category = validated_data.get('sub_category', instance.sub_category)
        instance.level = validated_data.get('level', instance.level)
        instance.save()

        _tags = request.DATA.getlist('tags[]')
        tags  = Tags.update_or_create(_tags)
        instance.tags.clear()
        instance.tags.add(*tags)

        return instance


