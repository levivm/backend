from django.conf import settings
from model_mommy import mommy

from referrals.models import Referral, Coupon, CouponType, Redeem
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
        self.referrer_type = mommy.make(CouponType, name='referrer')
        self.referred_type = mommy.make(CouponType, name='referred')

    def test_create(self):
        """
        Test to create the coupons
        """

        coupon_counter = Coupon.objects.count()
        redeem_counter = Coupon.objects.count()

        # Call the task
        task = CreateReferralCouponTask()
        task.delay(self.student.id, self.another_student.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter + 2)
        self.assertEqual(Redeem.objects.count(), redeem_counter + 2)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.referrer_type).exists())
        self.assertTrue(
            Redeem.objects.filter(student=self.another_student, coupon__coupon_type=self.referred_type).exists())

    def test_duplicate(self):
        """
        Test should not duplicate the coupons
        """

        referrer_coupon = mommy.make(Coupon, coupon_type=self.referrer_type)
        referred_coupon = mommy.make(Coupon, coupon_type=self.referred_type)
        mommy.make(Redeem, student=self.student, coupon=referrer_coupon)
        mommy.make(Redeem, student=self.another_student, coupon=referred_coupon)

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        # Call the task
        task = CreateReferralCouponTask()
        task.delay(self.student.id, self.another_student.id)

        self.assertEqual(Coupon.objects.count(), coupon_counter)
        self.assertEqual(Redeem.objects.count(), redeem_counter)
