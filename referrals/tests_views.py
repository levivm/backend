import urllib

import mock
from django.core.urlresolvers import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.authtoken.models import Token
from social.apps.django_app.default.models import UserSocialAuth

from referrals.factories import CouponFactory, RedeemFactory
from referrals.models import Referral, CouponType, Coupon, Redeem
from students.factories import StudentFactory
from students.models import Student
from users.factories import UserFactory
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
        self.signup_student_url = reverse('auth:signup_student')
        self.login_url = reverse('auth:login')
        self.social_login_signup_url = reverse('auth:social_login_signup', args=('facebook',))

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

    def get_new_user_data(self):
        return {
            'email': 'newstudent@example.com',
            'first_name': 'New',
            'last_name': 'Student',
            'password1': '12345678',
            'user_type': 'S'
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

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_send_invitation_mail(self, send_mail):
        """
        Test to send email with invitation
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': 'friend@example.com',
            'status': 'sent',
            'reject_reason': None
        }]

        # Anonymous should return unauthorized
        response = self.client.post(self.invite_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should not get the data
        response = self.organizer_client.post(self.invite_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.student_client.post(self.invite_url, {'emails': 'friend@example.com'})
        email_task = EmailTaskRecord.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(email_task.status, 'sent')

    def test_accept_invitation_view(self):
        """
        Test flow of viewing accept invitation
        """

        # Unexisting referrer code should return 404
        response = self.client.get(
            reverse('referrals:referrer', kwargs={'referrer_code': 'notexist'}))
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

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_accept_invitation_submit(self, send_mail):
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
        params = urllib.parse.urlencode(data, doseq=True)
        response = self.client.post(self.signup_student_url, data=params,
                                    content_type='application/x-www-form-urlencoded')
        new_student = Student.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_student.user.get_full_name(),
                         '%s %s' % (data['first_name'], data['last_name']))
        self.assertEqual(Referral.objects.count(), referral_counter + 1)
        self.assertEqual(Coupon.objects.count(), redeem_counter + 1)
        self.assertTrue(
            Referral.objects.filter(referrer=self.student, referred=new_student).exists())
        self.assertTrue(Coupon.objects.filter(coupon_type__name='referred').exists())
        self.assertTrue(Redeem.objects.filter(student=new_student,
                                              coupon__coupon_type__name='referred').exists())
        self.assertFalse(Redeem.objects.filter(student=self.student,
                                               coupon__coupon_type__name='referrer').exists())

    def test_invitation_blocked_ip(self):
        """
        Test to submit an invitation and is blocked by IP
        """
        ip_address = '192.0.1.12'

        # Objects
        mommy.make(Referral, _quantity=15, ip_address=ip_address)

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        data = self.get_new_user_data()
        response = self.client.post(self.signup_student_url, data, REMOTE_ADDR=ip_address)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Student.objects.filter(user__first_name=data['first_name']).exists())
        self.assertEqual(Referral.objects.count(), referral_counter)
        self.assertEqual(Coupon.objects.count(), redeem_counter)

    def test_login(self):
        """
        Test to login user and should not create referrals nor coupons
        """
        data = {
            'email': self.student.user.email,
            'password': self.password,
        }

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
        self.assertEqual(Referral.objects.count(), referral_counter)
        self.assertEqual(Coupon.objects.count(), redeem_counter)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_accept_invitation_facebook(self, get_json, send_mail):
        """
        Test to accept an invitation signing up by facebook
        """
        get_json.return_value = {
            'email': 'derivia@witcher.com',
            'first_name': 'Geralt',
            'last_name': 'De Rivia',
            'gender': 'male',
            'id': '123456789',
            'name': 'Geralt De Rivia',
        }

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        self.client.post(self.social_login_signup_url, {
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})
        new_student = Student.objects.latest('pk')
        self.assertEqual(Referral.objects.count(), referral_counter + 1)
        self.assertEqual(Coupon.objects.count(), redeem_counter + 1)
        self.assertTrue(
            Referral.objects.filter(referrer=self.student, referred=new_student).exists())
        self.assertTrue(Coupon.objects.filter(coupon_type__name='referred').exists())
        self.assertTrue(Redeem.objects.filter(student=new_student,
                                              coupon__coupon_type__name='referred').exists())

    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_dont_create_referral_if_exists(self, get_json):
        get_json.return_value = {
            'email': 'derivia@witcher.com',
            'first_name': 'Geralt',
            'last_name': 'De Rivia',
            'gender': 'male',
            'id': '123456789',
            'name': 'Geralt De Rivia',
        }

        student = StudentFactory()
        Token.objects.create(user=student.user)
        UserSocialAuth.objects.create(user=student.user, uid='123456789', provider='facebook')
        Referral.objects.create(referrer=self.student, referred=student, ip_address='127.0.0.1')

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        # Cookies
        self.client.cookies['refhash'] = self.student.get_referral_hash()

        self.client.post(self.social_login_signup_url, {
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})
        self.assertEqual(Referral.objects.count(), referral_counter)
        self.assertEqual(Coupon.objects.count(), redeem_counter)
        self.assertFalse(Redeem.objects.filter(student=student,
                                              coupon__coupon_type__name='referred').exists())

    @mock.patch('authentication.tasks.SendEmailConfirmEmailTask.delay')
    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_facebook_login(self, get_json, delay):
        """
        Test to login with Facebook and should not create referrals nor coupons
        """
        get_json.return_value = {
            'email': 'derivia@witcher.com',
            'first_name': 'Geralt',
            'last_name': 'De Rivia',
            'gender': 'male',
            'id': '123456789',
            'name': 'Geralt De Rivia',
        }

        # Counters
        referral_counter = Referral.objects.count()
        redeem_counter = Coupon.objects.count()

        response = self.client.post(self.social_login_signup_url, {
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})

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
        self.redeem = mommy.make(Redeem, student=self.student,
                                 coupon__coupon_type=self.referrer_type)

        # URLs
        self.validate_url = reverse('referrals:validate_coupon',
                                    kwargs={'coupon_code': self.redeem.coupon.token})

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
        self.assertEqual(response.data, {'amount': self.referrer_type.amount})

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

    def test_signup_success(self):
        """
        Test the global signup coupon
        """
        coupon = CouponFactory(coupon_type__type='global')
        coupon.token = 'GLOBAL-SIGNUP'
        coupon.save(update_fields=['token'])

        url = reverse('referrals:validate_coupon', kwargs={'coupon_code': 'GLOBAL-SIGNUP'})
        response = self.student_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signup_used(self):
        """
        Test the used global signup coupon
        """
        coupon = CouponFactory(coupon_type__type='global')
        coupon.token = 'GLOBAL-SIGNUP'
        coupon.save(update_fields=['token'])
        RedeemFactory(coupon=coupon, student=self.student, used=True)

        url = reverse('referrals:validate_coupon', kwargs={'coupon_code': 'GLOBAL-SIGNUP'})
        response = self.student_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
