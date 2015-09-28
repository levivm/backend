from django.conf import settings
from model_mommy import mommy
from referrals.models import Referral, Redeem, Coupon
from referrals.tasks import CreateReferralTask, CreateReferralCouponTask
from utils.tests import BaseAPITestCase


class CreateReferralTaskTest(BaseAPITestCase):
    """
    Class to test the CreateReferralTask
    """

    def setUp(self):
        super(CreateReferralTaskTest, self).setUp()

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        self.ip_address = '192.0.1.12'

    def test_create(self):
        """
        Test create the instance
        """

        # Counter
        referral_counter = Referral.objects.count()

        # Call the task
        task = CreateReferralTask()
        task.delay(self.student.id, self.another_student.id, self.ip_address)

        self.assertEqual(Referral.objects.count(), referral_counter + 1)
        self.assertTrue(Referral.objects.filter(referrer=self.student, referred=self.another_student,
                                                ip_address=self.ip_address).exists())

    def test_duplicate(self):
        """
        Test should not duplicated the referral
        """

        mommy.make(Referral, referrer=self.student, referred=self.another_student)

        # Counter
        referral_counter = Referral.objects.count()

        # Call the task
        task = CreateReferralTask()
        task.delay(self.student.id, self.another_student.id, self.ip_address)

        self.assertEqual(Referral.objects.count(), referral_counter)


class CreateReferralCouponTaskTest(BaseAPITestCase):
    """
    Class to test CreateReferralCouponTask
    """

    def setUp(self):
        super(CreateReferralCouponTaskTest, self).setUp()

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Coupons
        self.referrer_coupon = mommy.make(Coupon, name='referrer')
        self.referred_coupon = mommy.make(Coupon, name='referred')

    def test_create(self):
        """
        Test to create the coupons
        """

        redeem_counter = Redeem.objects.count()

        # Call the task
        task = CreateReferralCouponTask()
        task.delay(self.student.id, self.another_student.id)

        self.assertEqual(Redeem.objects.count(), redeem_counter + 2)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon=self.referrer_coupon).exists())
        self.assertTrue(Redeem.objects.filter(student=self.another_student, coupon=self.referred_coupon).exists())

    def test_duplicate(self):
        """
        Test should not duplicate the coupons
        """

        mommy.make(Redeem, student=self.student, coupon=self.referrer_coupon)
        mommy.make(Redeem, student=self.another_student, coupon=self.referred_coupon)

        # Counter
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = CreateReferralCouponTask()
        task.delay(self.student.id, self.another_student.id)

        self.assertEqual(Redeem.objects.count(), redeem_counter)
