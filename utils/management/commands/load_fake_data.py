import random

import factory
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from activities.factories import ActivityFactory, ActivityPhotoFactory, CalendarFactory, \
    CalendarSessionFactory
from activities.models import SubCategory
from orders.factories import OrderFactory, AssistantFactory, RefundFactory
from organizers.factories import OrganizerFactory, InstructorFactory, OrganizerBankInfoFactory
from payments.factories import FeeFactory
from referrals.factories import ReferralFactory, RedeemFactory, CouponTypeFactory
from reviews.factories import ReviewFactory
from students.factories import StudentFactory
from utils.management.commands import load_data


class Command(BaseCommand):
    help = "Load fake data"
    SAMPLES = [x for x in range(3, 6)]

    def handle(self, *args, **options):
        # Load data
        self.ask_for_load_data()

        # Users
        self.students = self.create_students()

        # Organizers
        self.organizers = self.create_organizers()
        self.instructors = self.create_instructors()
        self.bank_info = self.create_bank_info()

        # Activities
        self.subcategories = list(SubCategory.objects.all())
        self.activities = self.create_activities()
        self.activity_photos = self.create_activity_photos()
        self.calendars = self.create_calendars()
        self.calendar_sessions = self.create_calendar_sessions()

        # Orders
        self.orders = self.create_orders()
        self.assistants = self.create_assistants()
        self.refunds = self.create_refunds()

        # Referrals
        self.referral = self.create_referrals()
        self.redeem = self.create_redeems()

        # Reviews
        self.reviews = self.create_reviews()

    def ask_for_load_data(self):
        load = input('Este comando necesita primero correr load_data. ¿Desea correrlo ahora? (y/[n]): ')
        if load == 'y':
            load_data.Command().handle()

    def get_quantity(self):
        return random.choice(self.SAMPLES)

    @staticmethod
    def get_sample(array, quantity):
        return random.sample(array, quantity)

    @staticmethod
    def flat_list(array):
        return [item for sublist in array for item in sublist]

    def create_organizers(self):
        return OrganizerFactory.create_batch(self.get_quantity())

    def create_instructors(self):
        instructors = list()
        for organizer in self.organizers:
            quantity = self.get_quantity()
            instructors.append(InstructorFactory.create_batch(quantity, organizer=organizer))
        return self.flat_list(instructors)

    def create_students(self):
        return StudentFactory.create_batch(self.get_quantity())

    def create_activities(self):
        activities = list()
        for organizer in self.organizers:
            quantity = self.get_quantity()
            subcategories = self.get_sample(self.subcategories, quantity)
            instructors = list(organizer.instructors.all())
            instructors_sample = self.get_sample(instructors, len(instructors) - 1)
            activities.append(
                    ActivityFactory.create_batch(quantity, organizer=organizer,
                                                 sub_category=factory.Iterator(subcategories),
                                                 instructors=instructors_sample, location__organizer=organizer))

        return self.flat_list(activities)

    def create_activity_photos(self):
        photos = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            photos.append(ActivityPhotoFactory.create_batch(quantity, activity=activity))

        return self.flat_list(photos)

    def create_calendars(self):
        calendars = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            calendars.append(CalendarFactory.create_batch(quantity, activity=activity))

        return self.flat_list(calendars)

    def create_calendar_sessions(self):
        sessions = list()
        for calendar in self.calendars:
            quantity = self.get_quantity()
            sessions.append(CalendarSessionFactory.create_batch(quantity, calendar=calendar))

        return self.flat_list(sessions)

    def create_orders(self):
        orders = list()
        for student in self.students:
            quantity = self.get_quantity()
            calendars = self.get_sample(self.calendars, quantity)
            fee = self.create_fee()
            orders.append(
                    OrderFactory.create_batch(quantity, student=student, calendar=factory.Iterator(calendars),
                                              fee=fee)
            )

        return self.flat_list(orders)

    def create_assistants(self):
        assistants = list()
        for order in self.orders:
            quantity = self.get_quantity()
            assistants.append(AssistantFactory.create_batch(quantity, order=order))

        return self.flat_list(assistants)

    def create_refunds(self):
        quantity = self.get_quantity()
        users = self.get_sample(list(User.objects.all()), quantity)
        orders = self.get_sample(self.orders, quantity)
        assistants = [*self.get_sample(self.assistants, quantity - 1), None]

        return RefundFactory.create_batch(quantity, user=factory.Iterator(users), order=factory.Iterator(orders),
                                          assistant=factory.Iterator(assistants))

    def create_bank_info(self):
        return [OrganizerBankInfoFactory.create(organizer=o) for o in self.organizers]

    @staticmethod
    def create_fee():
        return FeeFactory()

    def create_referrals(self):
        quantity = 1
        referrer, referred = self.get_sample(self.students, quantity + 1)
        return ReferralFactory(referrer=referrer, referred=referred)

    def create_redeems(self):
        coupon_type = CouponTypeFactory()
        return RedeemFactory(student=self.referral.referred, coupon__coupon_type=coupon_type)

    def create_reviews(self):
        reviews = list()
        quantity = self.get_quantity()
        orders = self.get_sample(self.orders, quantity)
        for order in orders:
            reviews.append(ReviewFactory(activity=order.calendar.activity, author=order.student))

        return reviews
