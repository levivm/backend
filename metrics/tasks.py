import csv
import io

from celery import Task
from django.core.mail import EmailMultiAlternatives

from activities.models import Activity
from metrics.metrics import StudentGeneralRangeMetrics, OrganizerGeneralRangeMetrics
from orders.models import Order


class SendEmailGeneralMetricsExportTask(Task):
    def init(self, email, start_date, end_date, category):
        if category == 'students':
            self.get_data = self.get_student_data
            self.filename = 'metricas_generales_estudiantes.csv'
            self.csv_header = ['USERNAME', 'NOMBRE COMPLETO', 'EMAIL',
                               'TOTAL ACTIVIDADES COMPRADAS',
                               'ACTIVIDADES COMPRADAS "TITULO: (FECHA, CUPON)"', 'TOTAL COMPRADO']
        elif category == 'organizers':
            self.get_data = self.get_organizer_data
            self.filename = 'metricas_generales_organizadores.csv'
            self.csv_header = ['USERNAME', 'NOMBRE COMPLETO', 'EMAIL',
                               'ACTIVIDADES CREADAS "TITULO: (FECHA, ASISTENTES)"']
        else:
            raise Exception('Category unknown')

        self.email = email
        self.start_date = start_date
        self.end_date = end_date
        self.category = category

    def run(self, *args, **kwargs):
        self.init(*args, **kwargs)

        # Get the csv data from GeneralMetrics
        csv_data = self.get_csv(self.get_data())

        email_message = EmailMultiAlternatives(
            subject='Archivo csv',
            from_email='data@trulii.com',
            to=[self.email],
        )
        email_message.attach(self.filename, csv_data, 'text/csv')
        email_message.attach_alternative('Archivo csv', "text/html")
        return email_message.send()

    def get_student_data(self):
        def gen_data(students):
            for student in students:
                username = student.user.username
                full_name = student.user.get_full_name()
                email = student.user.email
                total_activities = Activity.objects.filter(
                    calendars__orders__student=student,
                    calendars__orders__status=Order.ORDER_APPROVED_STATUS).distinct('pk').count()
                orders = student.orders.select_related('calendar__activity') \
                    .filter(status=Order.ORDER_APPROVED_STATUS)
                activities_bought = '\n'.join(
                    ['%s: (%s; %s)' % (o.calendar.activity.title, o.created_at, o.coupon is None)
                     for o in orders])
                total_bought = sum(orders.values_list('amount', flat=True))
                yield [username, full_name, email, total_activities, activities_bought,
                       total_bought]

        general_metrics = StudentGeneralRangeMetrics(start_date=self.start_date,
                                                     end_date=self.end_date)
        students = general_metrics.get_recurrent_students(general_metrics.get_one_order_students())
        return gen_data(students)

    def get_organizer_data(self):
        def gen_data(organizers):
            for organizer in organizers:
                username = organizer.user.username
                full_name = organizer.user.get_full_name()
                email = organizer.user.email
                activities_created = ['%s: (%s; %s)' % (a.title, a.created_at,
                                                        len(a.get_assistants()))
                                      for a in organizer.activity_set.all()]
                yield [username, full_name, email, activities_created]

        general_metrics = OrganizerGeneralRangeMetrics(start_date=self.start_date,
                                                       end_date=self.end_date)
        organizers = general_metrics.get_recurrent_organizers(
            general_metrics.get_one_activity_organizers())
        return gen_data(organizers)

    def get_csv(self, data):
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(self.csv_header)
        writer.writerows(data)
        return csv_file.getvalue()
