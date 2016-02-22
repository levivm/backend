import mandrill
import mock
from celery import states
from django.conf import settings
from django.contrib.auth.models import User
from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory, ActivityFactory, CalendarSessionFactory
from activities.models import ActivityCeleryTaskEditActivity, \
    CalendarCeleryTaskEditActivity
from activities.tasks import SendEmailShareActivityTask, SendEmailCalendarTask, \
    SendEmailLocationTask
from orders.factories import AssistantFactory, OrderFactory
from orders.models import Order
from utils.models import EmailTaskRecord


class SendEmailCalendarTaskTest(APITestCase):
    """
    Class to test the SendEmailCalendarTask task
    """

    def setUp(self):
        self.calendar = CalendarFactory()
        self.sessions = CalendarSessionFactory.create_batch(2, calendar=self.calendar)
        self.order = OrderFactory(calendar=self.calendar, status=Order.ORDER_APPROVED_STATUS)
        self.assistants = AssistantFactory.create_batch(2, order=self.order)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_task_dispatch_if_there_is_not_other_task(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]

        task = SendEmailCalendarTask()
        task_id = task.delay(self.calendar.id)

        for assistant in self.assistants:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent').exists())

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

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_task_should_delete_on_success(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]
        task = SendEmailCalendarTask()
        task.delay(self.calendar.id)
        self.assertEqual(CalendarCeleryTaskEditActivity.objects.count(), 0)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_task_should_update_error_on_failure(self, send_mail):
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
        send_mail.side_effect = Exception('This could be a mandrill exception')
        task = SendEmailCalendarTask()
        task_id = task.delay(self.calendar.id)
        self.assertTrue(CalendarCeleryTaskEditActivity.objects.filter(
            task_id=task_id,
            state=states.FAILURE,
            calendar=self.calendar).exists())
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


class SendEmailShareActivityTaskTest(APITestCase):
    """
    Class to test the SendEmailShareActivityTask task
    """

    def setUp(self):
        self.user = mommy.make(User)
        self.activity = ActivityFactory()

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_success(self, send_mail):
        """
        Test send the email to share the activity when it's success
        """

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': e,
            'status': 'sent',
            'reject_reason': None
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='sent').exists())

    @mock.patch('utils.mixins.MandrillMixin.send_mail')
    def test_rejected(self, send_mail):
        """
        Test send the email to share the activity when it's rejected
        """

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': e,
            'status': 'rejected',
            'reject_reason': 'invalid-sender'
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='rejected',
                reject_reason='invalid-sender').exists())

    @mock.patch('utils.mixins.MandrillMixin.send_mail')
    def test_error(self, send_mail):
        """
        Test send the email to share the activity when it's error
        """

        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.side_effect = mandrill.Error('No subaccount exists with the id customer-123')

        # with self.assertRaises(mandrill.Error):
        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=email,
                status='error',
                reject_reason='No subaccount exists with the id customer-123').exists())

        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


class SendEmailLocationTaskTest(APITestCase):

    def setUp(self):
        self.activity = ActivityFactory()
        self.calendar = CalendarFactory(activity=self.activity)
        self.sessions = CalendarSessionFactory.create_batch(2, calendar=self.calendar)
        self.order = OrderFactory(calendar=self.calendar, status=Order.ORDER_APPROVED_STATUS)
        self.assistants = AssistantFactory.create_batch(2, order=self.order)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_task_dispatch_if_there_is_not_other_task(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]

        task = SendEmailLocationTask()
        task_id = task.delay(self.activity.id)

        for assistant in self.assistants:
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent').exists())

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

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_task_should_delete_on_success(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': assistant.email,
            'status': 'sent',
            'reject_reason': None
        } for assistant in self.assistants]
        task = SendEmailLocationTask()
        task.delay(self.activity.id)
        self.assertEqual(ActivityCeleryTaskEditActivity.objects.count(), 0)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_task_should_update_error_on_failure(self, send_mail):
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
        send_mail.side_effect = Exception('This could be a mandrill exception')
        task = SendEmailLocationTask()
        task_id = task.delay(self.activity.id)
        self.assertTrue(ActivityCeleryTaskEditActivity.objects.filter(
            task_id=task_id,
            state=states.FAILURE,
            activity=self.activity).exists())
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
