from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter

from activities.models import Activity, Tags, Category, SubCategory, ActivityPhoto, Calendar, CalendarSession, \
    ActivityStockPhoto, ActivityStats
from utils.mixins import OperativeModelAdminMixin


@admin.register(Category)
class CategoryAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name',)
    operative_readonly_fields = {'name', 'color'}


@admin.register(SubCategory)
class SubCategoryAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name','featured')
    search_fields = ['name', 'category__name']
    operative_readonly_fields = {'name', 'category'}


@admin.register(Activity)
class ActivityAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'organizer_name', 'next_calendar_initial_date',
                    'next_calendar_closing_sale', 'last_date', 'next_calendar_price',
                    'next_calendar_available_capacity')
    list_filter = ['published', 'organizer']
    search_fields = ('title', 'organizer__name')
    raw_id_fields = ('organizer', 'location')
    operative_readonly_fields = {'score', 'rating', 'last_date'}

    def organizer_name(self, obj):
        return obj.organizer.name

    def next_calendar_initial_date(self, obj):
        try:
            return obj.closest_calendar().initial_date
        except:
            return '-'

    def next_calendar_closing_sale(self, obj):
        try:
            return obj.closest_calendar().closing_sale
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
    list_display = ('initial_date', 'closing_sale', 'activity', 'session_price', 'num_enrolled')
    list_filter = ('initial_date', 'activity')
    operative_readonly_fields = {'number_of_sessions', 'initial_date'}

    def num_enrolled(self, obj):
        return obj.num_enrolled


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
