import datetime

from django.db.models import Q
from .models import Order



class OrderSearchEngine(object):

    def filter_query(self, query_params):
        activity = query_params.get('activity')
        from_date = query_params.get('from_date')
        until_date = query_params.get('until_date')
        status = query_params.get('status')
        order = query_params.get('id')

        query_id = Q(id=order) if order else None

        if query_id:
            return query_id

        query = Q()
        query = query & Q(calendar__activity_id=activity) if activity else query
        query = query & Q(status=status) if status else query




        if from_date is not None and until_date is not None:
            from_date = datetime.datetime.fromtimestamp(int(from_date) // 1000).\
                                          replace(second=0).date()
            until_date = datetime.datetime.fromtimestamp(int(until_date) // 1000).\
                                           replace(second=0).date()
            query = query & Q(created_at__range=[from_date, until_date])
        elif from_date is not None and until_date is None:
            from_date = datetime.datetime.fromtimestamp(int(from_date) // 1000).\
                                          replace(second=0).date()
            query = query & Q(created_at__gte=from_date)
        elif from_date is None and until_date is not None:
            until_date = datetime.datetime.fromtimestamp(int(until_date) // 1000).\
                                           replace(second=0).date()
            query = query & Q(created_at__lte=until_date)
        return query

    def get_by_organizer(self, organizer, filter_query=None):
        orders_q = Order.objects.select_related('calendar__activity', 'fee', 'student')
        if filter_query:
            orders = orders_q.filter(calendar__activity__organizer=organizer)\
                  .filter(filter_query)
        else:
            orders = orders_q.filter(calendar__activity__organizer=organizer)
        
        return orders

    def get_by_student(self, student, filter_query=None):

        orders_q = student.orders.select_related('calendar__activity', 'fee', 'student')

        if filter_query:
            orders = orders_q.filter(filter_query)
        else:
            orders = orders_q.all()
        
        return orders



