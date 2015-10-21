from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from model_mommy import mommy
from rest_framework import status

from referrals.models import Referral, CouponType, Coupon, Redeem
from students.models import Student
from utils.models import EmailTaskRecord
from utils.tests import BaseAPITestCase


class InviteAPITest(BaseAPITestCase):
    """
    Test the invite functionality
    """

    def setUp(self):
        super(InviteAPITest, self).setUp()

        # URLs
        self.invite_url = reverse('referrals:invite')
        self.referrer_url = self.student.get_referral_url()
        self.signup_login_url = reverse('users:signup_login')
        self.facebook_signup_login_url = reverse('facebook_signup_login')

        # User
        self.password = '12345678'
        self.student.user.email = 'student@email.com'
        self.student.user.set_password(self.password)
        self.student.user.save()

        self.another_student.user.email = 'another@email.com'
        self.another_student.user.set_password(self.password)
        self.another_student.user.save()

        # Coupons
        self.referrer_coupon = mommy.make(CouponType, name='referrer')
        self.referred_coupon = mommy.make(CouponType, name='referred')

        # SocialApp
        mommy.make(SocialApp,
                   name='trulii',
                   client_id='1563536137193781',
                   secret='9fecd238829796fd99109283aca7d4ff',
                   provider='facebook',
                   sites=[Site.objects.get(id=settings.SITE_ID)])

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

    def get_new_user_data(self):
        return {
            'email': 'newstudent@example.com',
            'first_name': 'New',
            'last_name': 'Student',
            'password1': '12345678',
            'user_type': 'S'
        }

    def get_login_data(self):
        return {
            'login': self.student.user.email,
            'password': self.password,
        }

    def get_facebook_data(self):
        return {
            'auth_token': "CAAWOByANCTUBAEU6rtjWRCdiv04HW7RqQnx9JVV8PWdUAlDjGn9fQh"
                          "ZCjHM0LEaTTv1U4vjH5A23zlZCUZAdDpUMyAgsf2veZCQQf4Y5FMcFUj"
                          "ZCLT2uNFlvCEBiTCaTcN5etZCF7xUSJlB4mqa7AZC87ZCb4amIh5QNf7"
                          "AIbIa13y5JAdbek0Ev"
        }

    def test_invite_page(self):
        """
        Test to get the invite info
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.invite_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should not get the data
        response = self.organizer_client.get(self.invite_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should get the invite data
        response = self.student_client.get(self.invite_url)
        self.assertContains(response, self.student.get_referral_url())

    def test_send_invitation_mail(self):
        """
        Test to send email with invitation
        """

        # Anonymous should return unauthorized
        response = self.client.post(self.invite_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should not get the data
        response = self.organizer_client.post(self.invite_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.student_client.post(self.invite_url, {'emails': 'friend@example.com'})
        email_task = EmailTaskRecord.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(email_task.send)
        self.assertEqual(email_task.data['name'], self.student.user.first_name)

    def test_accept_invitation_view(self):
        """
        Test flow of viewing accept invitation
        """

        # Unexisting referrer code should return 404
        response = self.client.get(reverse('referrals:referrer', kwargs={'referrer_code': 'notexist'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Anonymous should get the view
        response = self.client.get(self.referrer_url)
        self.assertContains(response, self.student.user.first_name)
        self.assertContains(response, self.student.get_referral_hash())

        # Student should get the view
        response = self.student_client.get(self.referrer_url)
        self.assertContains(response, self.student.user.first_name)
        self.assertContains(response, self.student.get_referral_hash())

        # Organizer should get the view
        response = self.organizer_client.get(self.referrer_url)
        self.assertContains(response, self.student.user.first_name)
        self.assertContains(response, self.student.get_referral_hash())

    def test_accept_invitation_submit(self):
        """
        Test to submit accepting the invitation
        """

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        # Anonymous should register and get the coupon
        data = self.get_new_user_data()
        response = self.client.post(self.signup_login_url, data)
        new_student = Student.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_student.user.get_full_name(), '%s %s' % (data['first_name'], data['last_name']))
        self.assertEqual(Referral.objects.count(), referral_counter + 1)
        self.assertEqual(Coupon.objects.count(), redeem_counter + 1)
        self.assertTrue(Referral.objects.filter(referrer=self.student, referred=new_student).exists())
        self.assertTrue(Coupon.objects.filter(coupon_type__name='referred').exists())
        self.assertTrue(Redeem.objects.filter(student=new_student, coupon__coupon_type__name='referred').exists())
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon__coupon_type__name='referrer').exists())

    def test_invitation_blocked_ip(self):
        """
        Test to submit an invitation and is blocked by IP
        """
        ip_address = '192.0.1.12'

        # Objects
        mommy.make(Referral, _quantity=3, ip_address=ip_address)

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        data = self.get_new_user_data()
        response = self.client.post(self.signup_login_url, data, REMOTE_ADDR=ip_address)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Student.objects.filter(user__first_name=data['first_name']).exists())
        self.assertEqual(Referral.objects.count(), referral_counter)
        self.assertEqual(Coupon.objects.count(), redeem_counter)

    def test_login(self):
        """
        Test to login user and should not create referrals nor coupons
        """
        data = self.get_login_data()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        response = self.client.post(self.signup_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
        self.assertEqual(Referral.objects.count(), referral_counter)
        self.assertEqual(Coupon.objects.count(), redeem_counter)

    def test_accept_invitation_facebook(self):
        """
        Test to accept an invitation signing up by facebook
        """
        data = self.get_facebook_data()

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        response = self.client.post(self.facebook_signup_login_url, data)
        new_student = Student.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
        self.assertEqual(Referral.objects.count(), referral_counter + 1)
        self.assertEqual(Coupon.objects.count(), redeem_counter + 1)
        self.assertTrue(Referral.objects.filter(referrer=self.student, referred=new_student).exists())
        self.assertTrue(Coupon.objects.filter(coupon_type__name='referred').exists())
        self.assertTrue(Redeem.objects.filter(student=new_student, coupon__coupon_type__name='referred').exists())

    def test_facebook_login(self):
        """
        Test to login with Facebook and should not create referrals nor coupons
        """
        data = self.get_facebook_data()

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        response = self.client.post(self.facebook_signup_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
        self.assertEqual(Referral.objects.count(), referral_counter)
        self.assertEqual(Coupon.objects.count(), redeem_counter)


class ValidateCouponTest(BaseAPITestCase):
    """
    Class to test if a coupon is valid
    """

    def setUp(self):
        super(ValidateCouponTest, self).setUp()

        # Coupons
        self.referrer_type = mommy.make(CouponType, name='referrer')
        self.redeem = mommy.make(Redeem, student=self.student, coupon__coupon_type=self.referrer_type)

        # URLs
        self.validate_url = reverse('referrals:validate_coupon', kwargs={'coupon_code': self.redeem.coupon.token})

    def test_valid(self):
        """
        Test if a coupon is valid
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.validate_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should return forbidden
        response = self.organizer_client.get(self.validate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should validate
        response = self.student_client.get(self.validate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_invalid(self):
        """
        Test if a coupon is invalid
        """

        self.redeem.set_used()

        response = self.student_client.get(self.validate_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_exist(self):
        """
        Test if a coupon doesn't exist
        """

        url = reverse('referrals:validate_coupon', kwargs={'coupon_code': 'REFERRAL-NONEXIST'})

        response = self.student_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
