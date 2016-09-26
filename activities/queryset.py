import datetime

from datetime import timedelta

import activities.constants as activities_constants
from django.db import connections, models
from django.db.models.sql.compiler import SQLCompiler


class NullsLastSQLCompiler(SQLCompiler):
    def get_order_by(self):
        result = super().get_order_by()
        if result and self.connection.vendor == 'postgresql':
            return [(expr, (sql + ' NULLS LAST', params, is_ref))
                    for (expr, (sql, params, is_ref)) in result]
        return result


class NullsLastQuery(models.sql.query.Query):
    """Use a custom compiler to inject 'NULLS LAST' (for PostgreSQL)."""

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return NullsLastSQLCompiler(self, connection, using)


class ActivityQuerySet(models.QuerySet):

    select_related_fields = ['organizer__user', 'sub_category__category', 'location__city']
    prefetch_related_fields = ['pictures', 'reviews__author__user',
                               'calendars__orders__student__user',
                               'calendars__orders__assistants']


    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.query = query or NullsLastQuery(self.model)


    def opened(self, *args, **kwargs):
        today = datetime.datetime.today().date()
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(calendars__initial_date__gte=today, 
                   calendars__enroll_open=True, published=True, *args, **kwargs).distinct()

    def closed(self, *args, **kwargs):
        today = datetime.datetime.today().date()
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            exclude(calendars__initial_date__gte=today, 
                   calendars__enroll_open=True, published=True).\
            filter(published=True, *args, **kwargs).distinct()

    def unpublished(self, *args, **kwargs):
        return self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(published=False, *args, **kwargs)

    def by_student(self, student, status=None, *args, **kwargs):
        activities_q = self.select_related(*self.select_related_fields).\
            prefetch_related(*self.prefetch_related_fields).\
            filter(calendars__orders__student=student).distinct()

        today = datetime.datetime.today().date()
        if status == activities_constants.NEXT:
            activities = activities_q.filter(calendars__initial_date__lt=today)
        elif status == activities_constants.CURRENT:
            activities = activities_q.filter(calendars__initial_date__gte=today)
        elif status == activities_constants.PAST:
            activities = activities_q.filter(calendars__initial_date__lt=today - timedelta(days=30))
        else:
            activities = activities_q.all()

        return activities

    def featured(self, *args, **kwargs):
        return self.filter(featured=True, *args, **kwargs)
