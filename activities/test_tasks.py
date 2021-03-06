import mock

from celery import states
from django.conf import settings
from model_mommy import mommy
from psycopg2.tests.test_types_extras import JsonbTestCase
from rest_framework.test import APITestCase

from django.utils.timezone import now, timedelta
from django.test import override_settings

from activities.factories import CalendarFactory, ActivityFactory, ActivityPhotoFactory
from activities.models import ActivityCeleryTaskEditActivity, \
    CalendarCeleryTaskEditActivity, ActivityStats
from activities.tasks import SendEmailShareActivityTask, SendEmailCalendarTask, \
    SendEmailLocationTask, ActivityViewsCounterTask, SendEmailSignUpLeadCouponTask
from locations.factories import LocationFactory
from orders.factories import AssistantFactory, OrderFactory
from orders.models import Order
from users.factories import UserFactory
from utils.models import EmailTaskRecord
from utils.serializers import HTMLField


class SendEmailCalendarTaskTest(APITestCase):
    """
    Class to test the SendEmailCalendarTask task
    """

    def setUp(self):
        self.calendar = CalendarFactory()
        self.order = OrderFactory(calendar=self.calendar, status=Order.ORDER_APPROVED_STATUS)
        self.assistants = AssistantFactory.create_batch(2, order=self.order)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_task_dispatch_if_there_is_not_other_task(self, send_mail):
        send_mail.return_value = [{
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]

        task = SendEmailCalendarTask()
        task_id = task.delay(self.calendar.id)
        html_field = HTMLField()

        context = {
            'organizer': self.calendar.activity.organizer.name,
            'activity': self.calendar.activity.title,
            'initial_date': self.calendar.initial_date.isoformat(),
            'schedules': html_field.to_representation(self.calendar.schedules),
            'price': self.calendar.session_price,
            'url_activity_id': '%sactivities/%s' % (settings.FRONT_SERVER_URL,
                                                    self.calendar.activity_id)
        }

        for assistant in self.assistants:
            data = {**context, 'name': assistant.first_name}
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent',
                data=data,
                template_name='activities/email/change_calendar_data.html').exists())

    def test_ignore_task_if_there_is_a_pending_task(self):
        CalendarCeleryTaskEditActivity.objects.create(
            task_id='05b9d438-821c-4506-9fa5-e958f3af406b',
            state=states.PENDING,
            calendar=self.calendar)

        task = SendEmailCalendarTask()
        task_id = task.delay(self.calendar.id)

        self.assertEqual(task_id.result, None)
        for assistant in self.assistants:
            self.assertFalse(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_task_should_delete_on_success(self, send_mail):
        send_mail.return_value = [{
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]
        task = SendEmailCalendarTask()
        task.delay(self.calendar.id)
        self.assertEqual(CalendarCeleryTaskEditActivity.objects.count(), 0)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False)
    def test_task_should_update_error_on_failure(self, send_mail):
        send_mail.side_effect = Exception('This could be a mandrill exception')
        task = SendEmailCalendarTask()
        task_id = task.delay(self.calendar.id)
        self.assertTrue(CalendarCeleryTaskEditActivity.objects.filter(
            task_id=task_id,
            state=states.FAILURE,
            calendar=self.calendar).exists())


class SendEmailShareActivityTaskTest(APITestCase):
    """
    Class to test the SendEmailShareActivityTask task
    """

    def setUp(self):
        self.user = UserFactory()
        self.activity = ActivityFactory(rating=4)
        self.calendar = CalendarFactory(activity=self.activity,
                                        initial_date=(now() + timedelta(days=5)).date())
        self.cover = ActivityPhotoFactory(activity=self.activity, main_photo=True)
        self.location = LocationFactory(organizer=self.activity.organizer)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail):
        """
        Test send the email to share the activity when it's success
        """
        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            'email': e,
            'status': 'sent',
            'reject_reason': None
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(user_id=self.user.id, activity_id=self.activity.id, emails=emails,
                             message=message)

        context = {
            'name': self.user.first_name,
            'activity': {
                'cover_url': self.cover.photo.url,
                'title': self.activity.title,
                'initial_date': self.activity.closest_calendar().initial_date.isoformat(),
            },
            'category': {
                'color': self.activity.sub_category.category.color,
                'name': self.activity.sub_category.category.name,
            },
            'message': message,
            'organizer': {
                'name': self.activity.organizer.name,
                'city': self.location.city.name,
            },
            'rating': self.activity.rating,
            # TODO quitar duration del template - FIXED
            # 'duration': self.activity.closest_calendar().duration // 3600,
            'price': self.activity.closest_calendar().session_price,
            'url': '%sactivities/%s/' % (settings.FRONT_SERVER_URL, self.activity.id),
        }

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='sent',
                data=context,
                template_name='activities/email/share_activity.html').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_rejected(self, send_mail):
        """
        Test send the email to share the activity when it's rejected
        """

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            'email': e,
            'status': 'rejected',
            'reject_reason': 'invalid-sender'
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(user_id=self.user.id, activity_id=self.activity.id, emails=emails,
                             message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='rejected',
                reject_reason='invalid-sender').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False)
    def test_error(self, send_mail):
        """
        Test send the email to share the activity when it's error
        """
        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.side_effect = Exception('No subaccount exists with the id customer-123')

        task = SendEmailShareActivityTask()
        task_id = task.delay(user_id=self.user.id, activity_id=self.activity.id, emails=emails,
                             message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='error',
                reject_reason='No subaccount exists with the id customer-123').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_anonymous_user(self, send_mail):
        """
        Test the task if the user is anonymous
        """
        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            'email': e,
            'status': 'sent',
            'reject_reason': None
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(activity_id=self.activity.id, user_name='Harvey', emails=emails,
                             message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='sent',
                data__name='Harvey',
                template_name='activities/email/share_activity.html').exists())


class SendEmailLocationTaskTest(APITestCase):

    def setUp(self):
        self.activity = ActivityFactory()
        self.calendar = CalendarFactory(activity=self.activity)
        self.order = OrderFactory(calendar=self.calendar, status=Order.ORDER_APPROVED_STATUS)
        self.assistants = AssistantFactory.create_batch(2, order=self.order)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_task_dispatch_if_there_is_not_other_task(self, send_mail):
        send_mail.return_value = [{
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]

        task = SendEmailLocationTask()
        task_id = task.delay(self.activity.id)

        context = {
            'organizer': self.activity.organizer.name,
            'activity': self.activity.title,
            'address': self.activity.location.address,
            'detail_url': self.activity.get_frontend_url(),
        }

        for assistant in self.assistants:
            data = {**context, 'name': assistant.first_name}
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent',
                data=data,
                template_name='activities/email/change_location_data.html').exists())

    def test_ignore_task_if_there_is_a_pending_task(self):
        ActivityCeleryTaskEditActivity.objects.create(
            task_id='05b9d438-821c-4506-9fa5-e958f3af406b',
            state=states.PENDING,
            activity=self.activity)

        task = SendEmailLocationTask()
        task_id = task.delay(self.activity.id)

        self.assertEqual(task_id.result, None)
        for assistant in self.assistants:
            self.assertFalse(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_task_should_delete_on_success(self, send_mail):
        send_mail.return_value = [{
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]
        task = SendEmailLocationTask()
        task.delay(self.activity.id)
        self.assertEqual(ActivityCeleryTaskEditActivity.objects.count(), 0)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False)
    def test_task_should_update_error_on_failure(self, send_mail):
        send_mail.side_effect = Exception('This could be a mandrill exception')
        task = SendEmailLocationTask()
        task_id = task.delay(self.activity.id)
        self.assertTrue(ActivityCeleryTaskEditActivity.objects.filter(
            task_id=task_id,
            state=states.FAILURE,
            activity=self.activity).exists())


class ActivityViewsCounterTaskTest(APITestCase):
    def setUp(self):
        self.activity = ActivityFactory()
        self.user = UserFactory()

    def test_run(self):
        task = ActivityViewsCounterTask()
        task.delay(activity_id=self.activity.id, user_id=self.user.id)

        self.assertEqual(self.activity.stats.views_counter, 1)

    def test_no_increment(self):
        """
        The counter shouldn't increment if the user is the
        activity's organizer
        """
        with self.assertRaises(ActivityStats.DoesNotExist):
            task = ActivityViewsCounterTask()
            task.delay(activity_id=self.activity.id, user_id=self.activity.organizer.user.id)
            self.assertEqual(self.activity.stats.views_counter, 0)


class SendEmailSignUpLeadCouponTaskTest(APITestCase):

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        send_mail.return_value = [{
            'email': 'kratos@godofwar.com',
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailSignUpLeadCouponTask()
        task_id = task.delay(email='kratos@godofwar.com')

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to='kratos@godofwar.com',
            status='sent',
            template_name='activities/email/new_lead_signup_coupon.html',
        ).exists())