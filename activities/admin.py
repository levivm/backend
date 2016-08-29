from django.contrib import admin, messages
from django.contrib.admin.filters import DateFieldListFilter
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from activities.models import Activity, Tags, Category, SubCategory, ActivityPhoto, Calendar, CalendarSession, \
    ActivityStockPhoto, ActivityStats
from utils.mixins import OperativeModelAdminMixin


@admin.register(Category)
class CategoryAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name',)
    operative_readonly_fields = {'name', 'color'}
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for category in queryset:
            category_name = category.name
            if Activity.objects.filter(sub_category__category=category).exists():
                self.message_user(request, 'La categoría %s no se puede eliminar porque tiene'
                                'actividades asociadas.' % category_name, level=messages.ERROR)
            else:
                category.delete()
                self.message_user(request, 'La categoría %s ha sido eliminada correctamente.' %
                                  category_name)

    def delete_view(self, request, object_id, extra_context=None):
        if request.POST:
            if Activity.objects.filter(sub_category__category__id=object_id).exists():
                self.message_user(request, 'La categoría no se puede eliminar porque tiene'
                                'actividades asociadas.', level=messages.ERROR)
                return redirect(reverse('admin:activities_category_change', args=(object_id,)))

        return super(CategoryAdmin, self).delete_view(request, object_id, extra_context)

    delete_selected.short_description = 'Eliminar category seleccionada/s'


@admin.register(SubCategory)
class SubCategoryAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name','featured')
    search_fields = ['name', 'category__name']
    operative_readonly_fields = {'name', 'category'}
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for subcategory in queryset:
            subcategory_name = subcategory.name
            if subcategory.activity_set.count() > 0:
                self.message_user(request, 'La subcategoría %s no se puede eliminar porque tiene'
                                'actividades asociadas.' % subcategory_name, level=messages.ERROR)
            else:
                subcategory.delete()
                self.message_user(request, 'La subcategoría %s ha sido eliminada correctamente.' %
                                  subcategory_name)

    def delete_view(self, request, object_id, extra_context=None):
        if request.POST:
            if Activity.objects.filter(sub_category_id=object_id).exists():
                self.message_user(request, 'La subcategoría no se puede eliminar porque tiene'
                                'actividades asociadas.', level=messages.ERROR)
                return redirect(reverse('admin:activities_subcategory_change', args=(object_id,)))

        return super(SubCategoryAdmin, self).delete_view(request, object_id, extra_context)

    delete_selected.short_description = 'Eliminar subcategory seleccionada/s'

@admin.register(Activity)
class ActivityAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'organizer_name', 'next_calendar_initial_date',
                    'last_date', 'next_calendar_price',
                    'next_calendar_available_capacity', 'id')
    list_filter = ['published', 'organizer']
    search_fields = ('id', 'title', 'organizer__name')
    raw_id_fields = ('organizer', 'location')
    operative_readonly_fields = {'score', 'rating', 'last_date'}

    def organizer_name(self, obj):
        return obj.organizer.name

    def next_calendar_initial_date(self, obj):
        try:
            return obj.closest_calendar().initial_date
        except:
            return '-'

    def next_calendar_price(self, obj):
        try:
            return obj.closest_calendar().session_price
        except:
            return '-'

    def next_calendar_available_capacity(self, obj):
        try:
            return obj.closest_calendar().available_capacity
        except:
            return '-'


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'occurrences')


@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('file_name', 'activity')
    list_filter = ['main_photo']
    search_fields = ['activity__title']
    operative_readonly_fields = {'activity'}

    def file_name(self, obj):
        return obj.photo.name

@admin.register(Calendar)
class CalendarAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('initial_date', 'enroll_open', 'activity_linkable', 'session_price', 'num_enrolled')
    list_filter = ('initial_date',)
    search_fields = ('activity__title',)
    operative_readonly_fields = {'number_of_sessions', 'initial_date'}

    def num_enrolled(self, obj):
        return obj.num_enrolled

    def activity_linkable(self, obj):
        url = reverse('admin:activities_activity_change', args=(obj.activity_id,))
        return '<a href="%s">%s</a>' % (url, obj.activity.title)

    activity_linkable.allow_tags = True
    activity_linkable.short_description = 'Activity'


@admin.register(CalendarSession)
class CalendarSessionAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'calendar', 'date')
    list_filter = ('date',)
    raw_id_fields = ('calendar',)
    operative_readonly_fields = {'date', 'calendar'}


@admin.register(ActivityStockPhoto)
class ActivityStockPhotoAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'id')
    list_filter = ['sub_category__name']
    search_fields = ['sub_category__name']

    def file_name(self, obj):
        return obj.photo.file.name


@admin.register(ActivityStats)
class ActivityStatsAdmin(admin.ModelAdmin):
    pass
