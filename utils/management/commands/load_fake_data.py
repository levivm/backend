import random

import factory
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from activities.factories import ActivityFactory, ActivityPhotoFactory, CalendarFactory, \
    CalendarSessionFactory
from activities.models import SubCategory, ActivityStockPhoto, ActivityPhoto, Tags
from locations.factories import CityFactory
from orders.factories import OrderFactory, AssistantFactory, RefundFactory
from organizers.factories import OrganizerFactory, InstructorFactory, OrganizerBankInfoFactory
from payments.factories import FeeFactory
from referrals.factories import ReferralFactory, RedeemFactory, CouponTypeFactory
from reviews.factories import ReviewFactory
from students.factories import StudentFactory
from students.models import Student
from utils.management.commands import load_data


class Command(BaseCommand):
    help = "Load fake data"
    students = None
    city = None
    organizers = None
    instructors = None
    bank_info = None
    subcategories = None
    activities = None
    activity_photos = None
    calendars = None
    calendar_sessions = None
    orders = None
    assistants = None
    refunds = None
    referral = None
    redeem = None
    reviews = None

    def add_arguments(self, parser):
        parser.add_argument('-l', '--load-data',
                            action='store_true',
                            default=False,
                            help='Load initial data before create fake data')
        parser.add_argument('-c', '--city',
                            default=False,
                            type=str,
                            help='The name of the city for the activities')
        parser.add_argument('-n', '--num-activities',
                            type=int,
                            help='The number of activities to create')

    def handle(self, *args, **options):
        # Load data
        self.ask_for_load_data(options['load_data'])

        # Users
        self.students = self.create_students()

        # Locations
        self.city = self.create_city(options['city'])

        # Organizers
        self.organizers = self.create_organizers()
        self.instructors = self.create_instructors()
        self.bank_info = self.create_bank_info()

        # Activities
        self.subcategories = list(SubCategory.objects.all())
        self.activities = self.create_activities(options.get('num_activities'))
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

    def ask_for_load_data(self, create_data):
        if create_data:
            self.stdout.write('Creando data inicial')
            load_data.Command().handle()

    @staticmethod
    def get_quantity(sample=range(3, 6)):
        return random.choice(sample)

    @staticmethod
    def get_sample(array, quantity):
        return random.sample(array, quantity)

    @staticmethod
    def flat_list(array):
        return [item for sublist in array for item in sublist]

    def create_city(self, city):
        if city:
            self.stdout.write('Creando ciudad')
            return CityFactory(name=city.capitalize())

    def create_organizers(self):
        self.stdout.write('Creando organizers')
        return OrganizerFactory.create_batch(self.get_quantity())

    def create_instructors(self):
        self.stdout.write('Creando instructors')
        instructors = list()
        for organizer in self.organizers:
            quantity = self.get_quantity()
            instructors.append(InstructorFactory.create_batch(quantity, organizer=organizer))
        return self.flat_list(instructors)

    def create_students(self):
        self.stdout.write('Creando students')
        return StudentFactory.create_batch(self.get_quantity())

    def create_activities(self, num_activities):
        self.stdout.write('Creando activities')
        activities = list()
        size = None

        if num_activities:
            size = num_activities // len(self.organizers)

        for organizer in self.organizers:
            quantity = size if size else self.get_quantity()
            instructors = list(organizer.instructors.all())
            instructors_sample = self.get_sample(instructors, 1)

            params = {
                'organizer': organizer,
                'published': True,
                'sub_category': factory.Iterator(self.subcategories),
                'instructors': instructors_sample,
                'location__organizer': organizer,
                'certification': factory.Faker('boolean'),
            }

            if self.city:
                params['location__city'] = self.city

            activities.append(ActivityFactory.create_batch(quantity, **params))

        activities = self.flat_list(activities)
        self.create_main_photo(activities)
        self.create_tags(activities)
        return activities

    def create_main_photo(self, activities):
        for activity in activities:
            try:
                stock_photo = random.choice(ActivityStockPhoto.objects.filter(sub_category=activity.sub_category))
                ActivityPhoto.objects.create(photo=stock_photo.photo,
                                             thumbnail=stock_photo.thumbnail,
                                             activity=activity, main_photo=True)
            except:
                pass

    def create_tags(self, activities):
        for activity in activities:
            subcategory_tag, _ = Tags.objects.get_or_create(name=activity.sub_category.name.lower())
            category_tag, _ = Tags.objects.get_or_create(name=activity.sub_category.category.name.lower())
            tags = [subcategory_tag, category_tag]
            activity.tags.add(*tags)

    def create_activity_photos(self):
        self.stdout.write('Creando activity photos')
        photos = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            photos.append(ActivityPhotoFactory.create_batch(quantity, activity=activity))

        return self.flat_list(photos)

    def create_calendars(self):
        self.stdout.write('Creando calendars')
        calendars = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            calendars.append(CalendarFactory.create_batch(quantity, activity=activity,
                                                          enroll_open=factory.Faker('boolean'),
                                                          is_weekend=factory.Faker('boolean'),
                                                          is_free=factory.Faker('boolean', chance_of_getting_true=20)))

        return self.flat_list(calendars)

    def create_calendar_sessions(self):
        self.stdout.write('Creando calendar sessions')
        sessions = list()
        for calendar in self.calendars:
            quantity = self.get_quantity()
            sessions.append(CalendarSessionFactory.create_batch(quantity, calendar=calendar))

        return self.flat_list(sessions)

    def create_orders(self):
        self.stdout.write('Creando orders')
        orders = list()
        fee = self.create_fee()
        for calendar in self.calendars:
            size = self.get_quantity()
            quantity = calendar.capacity // size
            if quantity < 1:
                continue
            orders.append(OrderFactory.create_batch(size, calendar=calendar,
                                                    student=factory.Iterator(Student.objects.all()),
                                                    fee=fee, quantity=quantity))

        return self.flat_list(orders)

    def create_assistants(self):
        self.stdout.write('Creando assistants')
        assistants = list()
        for order in self.orders:
            quantity = self.get_quantity(range(1, order.quantity + 1))
            assistants.append(AssistantFactory.create_batch(quantity, order=order))

        return self.flat_list(assistants)

    def create_refunds(self):
        self.stdout.write('Creando refunds')
        quantity = self.get_quantity()
        users = self.get_sample(list(User.objects.all()), quantity)
        orders = self.get_sample(self.orders, quantity)
        assistants = [*self.get_sample(self.assistants, quantity - 1), None]

        return RefundFactory.create_batch(quantity, user=factory.Iterator(users), order=factory.Iterator(orders),
                                          assistant=factory.Iterator(assistants))

    def create_bank_info(self):
        self.stdout.write('Creando bank infos')
        return [OrganizerBankInfoFactory.create(organizer=o) for o in self.organizers]

    @staticmethod
    def create_fee():
        return FeeFactory()

    def create_referrals(self):
        self.stdout.write('Creando referrals')
        quantity = 1
        referrer, referred = self.get_sample(self.students, quantity + 1)
        return ReferralFactory(referrer=referrer, referred=referred)

    def create_redeems(self):
        self.stdout.write('Creando redeems')
        coupon_type = CouponTypeFactory()
        return RedeemFactory(student=self.referral.referred, coupon__coupon_type=coupon_type)

    def create_reviews(self):
        self.stdout.write('Creando reviews')
        reviews = list()
        quantity = self.get_quantity()
        orders = self.get_sample(self.orders, quantity)
        for order in orders:
            reviews.append(ReviewFactory(activity=order.calendar.activity, author=order.student))

        return reviews
