from django.contrib import admin

from activities.models import Activity, Tags, Category, SubCategory, ActivityPhoto, Calendar, CalendarSession


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'category__name']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    pass


@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    pass


@admin.register(CalendarSession)
class CalendarSessionAdmin(admin.ModelAdmin):
    pass
