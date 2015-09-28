from django.test import TestCase
from model_mommy import mommy
from students.models import Student


class StudentTestModel(TestCase):

    def setUp(self):
        self.student = mommy.make(
            Student,
            user__username='student1',
            user__first_name='Student Number',
            user__last_name='One'
        )

    def test_referrer_code(self):
        self.assertEqual(self.student.referrer_code, 'studento1')
