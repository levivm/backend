from datetime import timedelta

from activities.models import Category
from orders.models import Order
from organizers.models import Organizer
from students.models import Student


class GeneralMetrics:
    def __init__(self, start_date, end_date):
        super(GeneralMetrics, self).__init__()
        self.start_date = start_date
        self.end_date = end_date + timedelta(days=1)
        self.range_metrics = self.get_range_metrics()
        self.total_metrics = self.get_total_metrics()

    def get_range_metrics(self):
        # Total Students
        total_students = Student.objects.filter(
            user__date_joined__range=(self.start_date, self.end_date)).count()

        # Recurrent Students
        one_order_students = Student.objects.filter(
            orders__created_at__range=(self.start_date, self.end_date),
            orders__status=Order.ORDER_APPROVED_STATUS).distinct()
        recurrent_students = Student.objects.filter(id__in=one_order_students,
                                                    orders__created_at__lt=self.start_date,
                                                    orders__status=Order.ORDER_APPROVED_STATUS) \
            .distinct().count()

        # Total Organizers
        total_organizers = Organizer.objects.filter(
            user__date_joined__range=(self.start_date, self.end_date)) \
            .count()

        # Recurrent Organizers
        one_activity_organizers = Organizer.objects.filter(
            activity__created_at__range=(self.start_date, self.end_date),
            activity__published=True).distinct()
        recurrent_organizers = Organizer.objects.filter(id__in=one_activity_organizers,
                                                        activity__created_at__lt=(self.start_date),
                                                        activity__published=True) \
            .distinct().count()

        # Students & Organizers by category
        numbers_by_category = list()
        for category in Category.objects.all():
            num_students = Student.objects.filter(
                orders__calendar__activity__sub_category__category=category,
                orders__created_at__range=(self.start_date, self.end_date),
                orders__status=Order.ORDER_APPROVED_STATUS).distinct().count()
            num_organizers = Organizer.objects.filter(
                activity__created_at__range=(self.start_date, self.end_date),
                activity__sub_category__category=category).distinct().count()
            numbers_by_category.append([category.name, num_students, num_organizers])

        return {
            'students': [
                ['Total', total_students],
                ['Recurrentes', recurrent_students],
                ['1+ Inscripciones', one_order_students.count()],
            ],
            'organizers': [
                ['Total', total_organizers],
                ['Recurrentes', recurrent_organizers],
                ['1+ Actividades', one_activity_organizers.count()],
            ],
            'numbers_by_category': numbers_by_category,
        }

    def get_total_metrics(self):
        # Total Students
        total_students = Student.objects.count()

        # Total Organizers
        total_organizers = Organizer.objects.count()

        # Total Orders
        total_orders = Order.objects.filter(status=Order.ORDER_APPROVED_STATUS).count()

        return {
            'total_students': total_students,
            'total_organizers': total_organizers,
            'total_orders': total_orders,
        }
