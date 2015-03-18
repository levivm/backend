# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"
from django.shortcuts import render_to_response
from serializers import ActivitiesSerializer,CategoriesSerializer,SubCategoriesSerializer,\
                        TagsSerializer, ChronogramsSerializer,ActivityPhotosSerializer
from models import Activity,Category,SubCategory,Tags,Chronogram,ActivityPhoto
from rest_framework import viewsets,status
from rest_framework.parsers import FileUploadParser
from django.utils.translation import ugettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime
from utils.forms import FileUploadForm
from utils.form_utils import ajax_response
from django.conf import settings




class ChronogramsViewSet(viewsets.ModelViewSet):
    serializer_class = ChronogramsSerializer
    #queryset = Chronogram.objects.all()
    lookup_url_kwarg = 'calendar_pk'


    def get_queryset(self):
        activity_id = self.kwargs.get('activity_pk',None)
        activity = get_object_or_404(Activity,pk=activity_id)
        return activity.chronogram_set.all()



class ActivitiesViewSet(viewsets.ModelViewSet):
    #parser_classes = (FileUploadParser,)
    
    queryset = Activity.objects.all()
    serializer_class = ActivitiesSerializer
    #permission_classes = (IsOwnerOrReadOnly,)

    # def list(self, request):
    #     queryset = Activity.objects.all()
    #     serializer = ActivitiesSerializer(queryset, many=True)
    #     return Response(serializer.data)

    # def retrieve(self, request, pk=None):
    #     queryset = Activity.objects.all()
    #     activities = get_object_or_404(queryset, pk=pk)
    #     serializer = ActivitiesSerializer(activities)


    def delete_calendar(self,request,pk=None):


        chronogram_id = request.GET.get('id',None)

        activity   = self.get_object()
        try:
            chronogram = activity.chronogram_set.get(id=chronogram_id)
        except Chronogram.DoesNotExist:
            msg = _("El Calendario a borrar no existe")
            return Response({str(chronogram_id):msg},status=status.HTTP_404_NOT_FOUND)

        chronogram.delete()
        return Response({'chronogram_id':chronogram_id},status=status.HTTP_200_OK)


    def get_calendars(self,request,pk=None):
        print "AQUIIIIIIIIIIII NOOOOOOOOO"
        activity   = self.get_object()
        chronogram = activity.chronogram_set.all()
        chronogram_serializer = chronogram_serializer = ChronogramsSerializer(chronogram,many=True)

        return Response(chronogram_serializer.data)
         
    def update_calendar(self,request,pk=None):

        data = request.DATA
        chronogram_id = data.get("id",None)
        activity   = self.get_object()

        try:
            chronogram = activity.chronogram_set.get(id=chronogram_id)
        except Chronogram.DoesNotExist:
            msg = _("El calendario a editar no existe")
            return Response({'non_field_errors':[msg]},status=status.HTTP_404_NOT_FOUND)

        chronogram = activity.chronogram_set.get(id=chronogram_id)
        chronogram_serializer = ChronogramsSerializer(chronogram,data=data,context={'request':request})
        chronogram = None
        if chronogram_serializer.is_valid(raise_exception=True):
            chronogram = chronogram_serializer.save()
        print "Chronogram",chronogram
        return Response(chronogram_serializer.data) 

    def create_calendar(self,request,pk=None):

        data  = request.DATA        


        chronogram_serializer = ChronogramsSerializer(data=data,context={'request':request})
        chronogram = None
        if chronogram_serializer.is_valid(raise_exception=True):
            chronogram = chronogram_serializer.save()
        print "Chronogram",chronogram
        return Response(chronogram_serializer.data)         


    def add_photo(self,request,pk=None):

        activity = self.get_object()

        photos_count = activity.photos.count()
        print "POHOHOOHOOTOOTOS ",photos_count

        if photos_count >= settings.MAX_ACTIVITY_PHOTOS:
            msg = _(u'Ya excedió el número máximo de imagenes por actividad')
            return Response({'non_field_errors':[msg]},status=status.HTTP_404_NOT_FOUND)

        photo    = None
        #return Response({'photo_id':1})
        file_form = FileUploadForm(request.POST,request.FILES)
        if file_form.is_valid():
            photo = file_form.cleaned_data['file']
            activity_photo = ActivityPhoto(photo=photo,activity=activity)
            activity_photo.save()
            activity_serializer = ActivitiesSerializer(instance=activity,context={'request':request})
            photo_serializer = ActivityPhotosSerializer(instance=activity_photo)
            return Response({'activity':activity_serializer.data,'photo':photo_serializer.data})
        else:
            return Response(ajax_response(file_form),status=status.HTTP_406_NOT_ACCEPTABLE)


    def delete_photo(self,request,pk=None):
        activity = self.get_object()
        photo_id = request.DATA.get("photo_id",None)
        try:
            photo = activity.photos.get(id=photo_id)
            photo.delete()
            activity_serializer = ActivitiesSerializer(instance=activity,context={'request':request})
            return Response({'photo_id':photo_id,'activity':activity_serializer.data},status=status.HTTP_200_OK)
        except ActivityPhoto.DoesNotExist:
            msg = _("La imagen a eliminar no existe")
            return Response({'non_field_errors':[msg]},status=status.HTTP_404_NOT_FOUND)




    def general_info(self,request):
        categories     = Category.objects.all()
        sub_categories = SubCategory.objects.all()
        tags   = Tags.ready_to_use()
        types  = Activity.get_types()
        levels = Activity.get_levels()

        data = {
            'categories':CategoriesSerializer(categories,many=True).data,
            'subcategories':SubCategoriesSerializer(sub_categories,many=True).data,
            'types':types,
            'levels':levels,
            'tags':TagsSerializer(tags,many=True).data,
        }

        return Response(data)
        



class CategoriesViewSet(viewsets.ModelViewSet): 
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer



class SubCategoriesViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoriesSerializer

    

    # def create():


    # def perform_create(self, serializer):
    #     print "Category",self.request.POST.get('category_id')
    #     print self.request.POST.get('category_id')
    #     category = get_object_or_404(Category, id=1)
        
    #     serializer.save(category=category)
        

class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class ListCategories(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        categories    = Category.objects.all()
        subcategories = SubCategory.objects.all()
        data = {
            'categories':CategoriesSerializer(categories,many=True).data,
            'subcategory':SubCategoriesSerializer(subcategories,many=True).data,
        }
        return Response(data)

