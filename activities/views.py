
from django.shortcuts import render_to_response
from serializers import ActivitiesSerializer,CategoriesSerializer,SubCategoriesSerializer,TagsSerializer
from models import Activity,Category,SubCategory,Tags
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class ActivitiesViewSet(viewsets.ModelViewSet):

    
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
        
    def pre_save(request,obj):
        print "OBBJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ",obj



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