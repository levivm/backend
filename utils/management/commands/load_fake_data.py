import random
from itertools import cycle

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from model_mommy import mommy
from model_mommy.recipe import related

from activities.models import SubCategory


class Command(BaseCommand):
    help = "Load fake data"
    SAMPLES = [x for x in range(3, 6)]

    def handle(self, *args, **options):
        # Users
        self.students = self.create_students()

        # Organizers
        self.organizers = self.create_organizers()
        self.instructors = self.create_instructors()
        self.banks_info = self.create_banks_info()

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

        # Payments
        self.fee = self.create_fee()

        # Referrals
        self.referral = self.create_referrals()
        self.redeem = self.create_redeems()

        # Reviews
        self.reviews = self.create_reviews()

    def get_quantity(self):
        return random.choice(self.SAMPLES)

    def get_sample(self, array, quantity):
        return random.sample(array, quantity)

    def flat_list(self, array):
        return [item for sublist in array for item in sublist]

    def create_organizers(self):
        organizers = list()
        quantity = self.get_quantity()
        for i in range(quantity):
            organizers.append(mommy.make_recipe('organizers.organizer'))

        return organizers

    def create_instructors(self):
        instructors = list()
        for organizer in self.organizers:
            quantity = self.get_quantity()
            instructors.append(mommy.make_recipe('organizers.instructor', _quantity=quantity, organizer=organizer))

        return self.flat_list(instructors)

    def create_students(self):
        students = list()
        quantity = self.get_quantity()
        for i in range(quantity):
            students.append(mommy.make_recipe('students.student'))

        return students

    def create_activities(self):
        activities = list()
        for organizer in self.organizers:
            quantity = self.get_quantity()
            subcategories = self.get_sample(self.subcategories, quantity)
            instructors = list(organizer.instructors.all())
            instructors_sample = self.get_sample(instructors, len(instructors) - 1)
            tags = self.create_tags()
            activities.append(mommy.make_recipe('activities.activity', _quantity=quantity, organizer=organizer,
                                                sub_category=cycle(subcategories), instructors=instructors_sample,
                                                tags=tags))
        return self.flat_list(activities)

    def create_tags(self):
        tags = list()
        for i in range(2):
            tags.append(mommy.make_recipe('activities.tag'))

        return tags

    def create_activity_photos(self):
        photos = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            photos.append(mommy.make_recipe('activities.activity_photo', _quantity=quantity, activity=activity))

        return self.flat_list(photos)

    def create_calendars(self):
        calendars = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            calendars.append(mommy.make_recipe('activities.calendar', _quantity=quantity, activity=activity))

        return self.flat_list(calendars)

    def create_calendar_sessions(self):
        sessions = list()
        for calendar in self.calendars:
            quantity = self.get_quantity()
            sessions.append(mommy.make_recipe('activities.calendar_session', _quantity=quantity, calendar=calendar))

        return self.flat_list(sessions)

    def create_orders(self):
        orders = list()
        for student in self.students:
            quantity = self.get_quantity()
            calendars = self.get_sample(self.calendars, quantity)
            for calendar in calendars:
                orders.append(
                        mommy.make_recipe('orders.order', student=student, calendar=calendar)
                )

        return orders

    def create_assistants(self):
        assistants = list()
        for order in self.orders:
            quantity = self.get_quantity()
            assistants.append(mommy.make_recipe('orders.assistant', _quantity=quantity, order=order))

        return self.flat_list(assistants)

    def create_refunds(self):
        quantity = self.get_quantity()
        users = self.get_sample(list(User.objects.all()), quantity)
        orders = self.get_sample(self.orders, quantity)
        assistants = [*self.get_sample(self.assistants, quantity - 1), None]

        return mommy.make_recipe('orders.refund', _quantity=quantity, user=cycle(users), order=cycle(orders),
                                 assistant=cycle(assistants))

    def create_banks_info(self):
        bank_info = list()
        for organizer in self.organizers:
            bank_info.append(
                mommy.make_recipe('organizers.organizer_bank_info', organizer=organizer))

        return bank_info

    def create_fee(self):
        return mommy.make_recipe('payments.fee')

    def create_referrals(self):
        quantity = 1
        students = self.get_sample(self.students, quantity + 1)
        return mommy.make_recipe('referrals.referral', referred=students[0], referrer=students[1])

    def create_redeems(self):
        return mommy.make_recipe('referrals.redeem', student=self.referral.referred)

    def create_reviews(self):
        reviews = list()
        quantity = self.get_quantity()
        orders = self.get_sample(self.orders, quantity)
        for order in orders:
            reviews.append(mommy.make_recipe('reviews.review', activity=order.calendar.activity, author=order.student))

        return reviews
