from django.contrib import admin

from reviews.models import Review
from utils.mixins import OperativeModelAdminMixin


@admin.register(Review)
class ReviewAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'activity', 'author', 'replied_at', 'rating'}
