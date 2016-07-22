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
        self.student_general_range_metrics = StudentGeneralRangeMetrics(start_date=start_date,
                                                                        end_date=end_date)
        self.organizer_general_range_metrics = OrganizerGeneralRangeMetrics(start_date=start_date,
                                                                            end_date=end_date)

    def get_range_metrics(self):
        # Total Students
        # total_students = Student.objects.filter(
        #     user__date_joined__range=(self.start_date, self.end_date)).count()
        #
        # # Recurrent Students
        # one_order_students = Student.objects.filter(
        #     orders__created_at__range=(self.start_date, self.end_date),
        #     orders__status=Order.ORDER_APPROVED_STATUS).distinct()
        # recurrent_students = Student.objects.filter(id__in=one_order_students,
        #                                             orders__created_at__lt=self.start_date,
        #                                             orders__status=Order.ORDER_APPROVED_STATUS) \
        #     .distinct().count()

        # # Total Organizers
        # total_organizers = Organizer.objects.filter(
        #     user__date_joined__range=(self.start_date, self.end_date)) \
        #     .count()
        #
        # # Recurrent Organizers
        # one_activity_organizers = Organizer.objects.filter(
        #     activity__created_at__range=(self.start_date, self.end_date),
        #     activity__published=True).distinct()
        # recurrent_organizers = Organizer.objects.filter(id__in=one_activity_organizers,
        #                                                 activity__created_at__lt=(self.start_date),
        #                                                 activity__published=True) \
        #     .distinct().count()

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
            'students': self.student_general_range_metrics.get_range(),
            'organizers':self.organizer_general_range_metrics.get_range(),
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


class StudentGeneralRangeMetrics:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_range(self):
        # Total Students
        total_students = self.get_total_students()

        # Recurrent Students
        one_order_students = self.get_one_order_students()
        recurrent_students = self.get_recurrent_students(one_order_students=one_order_students)

        return [
            ['Total', total_students],
            ['Recurrentes', recurrent_students.count()],
            ['1+ Inscripciones', one_order_students.count()],
        ]

    def get_total_students(self):
        return Student.objects.filter(
            user__date_joined__range=(self.start_date, self.end_date)).count()

    def get_one_order_students(self):
        return Student.objects.filter(
            orders__created_at__range=(self.start_date, self.end_date),
            orders__status=Order.ORDER_APPROVED_STATUS).distinct()

    def get_recurrent_students(self, one_order_students):
        return Student.objects.filter(id__in=one_order_students,
                                      orders__created_at__lt=self.start_date,
                                      orders__status=Order.ORDER_APPROVED_STATUS) \
            .distinct()


class OrganizerGeneralRangeMetrics:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_range(self):
        # Total Organizers
        total_organizers = self.get_total_organizers()

        # Recurrent Organizers
        one_activity_organizers = self.get_one_activity_organizers()
        recurrent_organizers = self.get_recurrent_organizers(
            one_activity_organizers=one_activity_organizers)

        return [
            ['Total', total_organizers],
            ['Recurrentes', recurrent_organizers.count()],
            ['1+ Actividades', one_activity_organizers.count()],
        ]

    def get_total_organizers(self):
        return Organizer.objects.filter(
            user__date_joined__range=(self.start_date, self.end_date)).count()

    def get_one_activity_organizers(self):
        return Organizer.objects.filter(
            activity__created_at__range=(self.start_date, self.end_date),
            activity__published=True).distinct()

    def get_recurrent_organizers(self, one_activity_organizers):
        return Organizer.objects.filter(id__in=one_activity_organizers,
                                                        activity__created_at__lt=(self.start_date),
                                                        activity__published=True) \
            .distinct()
