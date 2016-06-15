from django.contrib import admin

from activities.models import Activity, Tags, Category, SubCategory, ActivityPhoto, Calendar, CalendarSession, \
    ActivityStockPhoto, ActivityStats
from utils.mixins import OperativeModelAdminMixin


@admin.register(Category)
class CategoryAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'name', 'color'}


@admin.register(SubCategory)
class SubCategoryAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    search_fields = ['name', 'category__name']
    operative_readonly_fields = {'name', 'category'}


@admin.register(Activity)
class ActivityAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    search_fields = ('title',)
    raw_id_fields = ('organizer', 'location')
    operative_readonly_fields = {'score', 'rating', 'last_date'}


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    pass


@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'activity'}


@admin.register(Calendar)
class CalendarAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'number_of_sessions', 'initial_date'}


@admin.register(CalendarSession)
class CalendarSessionAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    raw_id_fields = ('calendar',)
    operative_readonly_fields = {'date', 'calendar'}


@admin.register(ActivityStockPhoto)
class ActivityStockPhotoAdmin(admin.ModelAdmin):
    search_fields = ['sub_category__name']


@admin.register(ActivityStats)
class ActivityStatsAdmin(admin.ModelAdmin):
    pass
