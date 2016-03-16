import random
from typing import Optional, Any, List

import factory
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from activities.factories import ActivityFactory, ActivityPhotoFactory, CalendarFactory, \
    CalendarSessionFactory
from activities.models import SubCategory, ActivityStockPhoto, ActivityPhoto, Tags, Activity, \
    Calendar, CalendarSession
from locations.factories import CityFactory, LocationFactory
from locations.models import City, Location
from orders.factories import OrderFactory, AssistantFactory, RefundFactory
from orders.models import Order, Assistant, Refund
from organizers.factories import OrganizerFactory, InstructorFactory, OrganizerBankInfoFactory
from organizers.models import Organizer, Instructor, OrganizerBankInfo
from payments.factories import FeeFactory
from payments.models import Fee
from referrals.factories import ReferralFactory, RedeemFactory, CouponTypeFactory
from referrals.models import Referral, Redeem
from reviews.factories import ReviewFactory
from reviews.models import Review
from students.factories import StudentFactory
from students.models import Student
from utils.management.commands import load_data


class Command(BaseCommand):
    help = "Load fake data"

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

        # Locations
        self.city = self.create_city(options['city'].strip())
        self.locations = self.create_locations()

        # Users
        self.students = self.create_students()

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

    def ask_for_load_data(self, create_data: bool) -> None:
        if create_data:
            self.stdout.write('Creando data inicial')
            load_data.Command().handle()

    @staticmethod
    def get_quantity(sample: iter = range(3, 6)) -> int:
        return random.choice(sample)

    @staticmethod
    def get_sample(iterable: list, quantity: int) -> Any:
        return random.sample(iterable, quantity)

    @staticmethod
    def flat_list(iterable: list) -> list:
        return [item for sublist in iterable for item in sublist]

    def create_city(self, city: str) -> Optional[City]:
        if city:
            self.stdout.write('Creando ciudad')
            return CityFactory(name=city.capitalize())

    def create_locations(self) -> List[Location]:
        self.stdout.write('Creado locations')
        params = {'city': self.city} if self.city else {}
        return LocationFactory.create_batch(self.get_quantity(), **params)

    def create_organizers(self) -> List[Organizer]:
        self.stdout.write('Creando organizers')
        return OrganizerFactory.create_batch(self.get_quantity())

    def create_instructors(self) -> List[Instructor]:
        self.stdout.write('Creando instructors')
        instructors = list()
        for organizer in self.organizers:
            quantity = self.get_quantity()
            instructors.append(InstructorFactory.create_batch(quantity, organizer=organizer))
        return self.flat_list(instructors)

    def create_students(self) -> List[Student]:
        self.stdout.write('Creando students')
        params = {'city': self.city} if self.city else {}
        return StudentFactory.create_batch(self.get_quantity(), **params)

    def create_activities(self, num_activities: int) -> List[Activity]:
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
                'sub_category': factory.Iterator(self.subcategories, cycle=True),
                'instructors': instructors_sample,
                'location': factory.Iterator(self.locations, cycle=True),
                'certification': factory.Faker('boolean'),
            }

            activities.append(ActivityFactory.create_batch(quantity, **params))

        activities = self.flat_list(activities)
        self.create_main_photo(activities)
        self.create_tags(activities)
        return activities

    def create_main_photo(self, activities: List[Activity]) -> None:
        for activity in activities:
            try:
                stock_photo = random.choice(
                    ActivityStockPhoto.objects.filter(sub_category=activity.sub_category))
                ActivityPhoto.objects.create(photo=stock_photo.photo,
                                             thumbnail=stock_photo.thumbnail,
                                             activity=activity, main_photo=True)
            except:
                pass

    def create_tags(self, activities: List[Activity]) -> None:
        for activity in activities:
            subcategory_tag, _ = Tags.objects.get_or_create(
                name=activity.sub_category.name.lower())
            category_tag, _ = Tags.objects.get_or_create(
                name=activity.sub_category.category.name.lower())
            tags = [subcategory_tag, category_tag]
            activity.tags.add(*tags)

    def create_activity_photos(self) -> List[ActivityPhoto]:
        self.stdout.write('Creando activity photos')
        photos = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            photos.append(ActivityPhotoFactory.create_batch(quantity, activity=activity))

        return self.flat_list(photos)

    def create_calendars(self) -> List[Calendar]:
        self.stdout.write('Creando calendars')
        calendars = list()
        for activity in self.activities:
            quantity = self.get_quantity()
            calendars.append(
                CalendarFactory.create_batch(quantity,
                                             activity=activity,
                                             enroll_open=factory.Faker('boolean'),
                                             is_weekend=factory.Faker('boolean'),
                                             is_free=factory.Faker('boolean',
                                                                   chance_of_getting_true=20)))

        return self.flat_list(calendars)

    def create_calendar_sessions(self) -> List[CalendarSession]:
        self.stdout.write('Creando calendar sessions')
        sessions = list()
        for calendar in self.calendars:


            quantity = self.get_quantity()
            sessions.append(CalendarSessionFactory.create_batch(quantity, calendar=calendar))
            activity = calendar.activity
            sessions_data = [s for s in calendar.sessions.all()]
            if sessions_data:
                last_session = sorted(sessions_data, key=lambda s: s.date, reverse=True)[0]
                last_session = {'date':last_session.date} 
                activity.set_last_date(last_session)

        return self.flat_list(sessions)

    def create_orders(self) -> List[Order]:
        self.stdout.write('Creando orders')
        orders = list()
        fee = self.create_fee()
        for calendar in self.calendars:
            size = self.get_quantity()
            quantity = calendar.capacity // size
            if quantity < 1:
                continue
            orders.append(OrderFactory.create_batch(size, calendar=calendar,
                                                    student=factory.Iterator(
                                                        Student.objects.all(), cycle=True),
                                                    fee=fee, quantity=quantity))

        return self.flat_list(orders)

    def create_assistants(self) -> List[Assistant]:
        self.stdout.write('Creando assistants')
        assistants = list()
        for order in self.orders:
            quantity = self.get_quantity(range(1, order.quantity + 1))
            assistants.append(AssistantFactory.create_batch(quantity, order=order))

        return self.flat_list(assistants)

    def create_refunds(self) -> List[Refund]:
        self.stdout.write('Creando refunds')
        quantity = self.get_quantity()
        users = self.get_sample(list(User.objects.all()), quantity)
        orders = self.get_sample(self.orders, quantity)
        assistants = [*self.get_sample(self.assistants, quantity - 1), None]

        return RefundFactory.create_batch(quantity, user=factory.Iterator(users, cycle=True),
                                          order=factory.Iterator(orders, cycle=True),
                                          assistant=factory.Iterator(assistants, cycle=True))

    def create_bank_info(self) -> List[OrganizerBankInfo]:
        self.stdout.write('Creando bank infos')
        size = len(self.organizers)
        organizers = factory.Iterator(self.organizers)
        return OrganizerBankInfoFactory.create_batch(size, organizer=organizers)

    def create_fee(self) -> Fee:
        self.stdout.write('Creando fee')
        return FeeFactory()

    def create_referrals(self) -> Referral:
        self.stdout.write('Creando referrals')
        quantity = 1
        referrer, referred = self.get_sample(self.students, quantity + 1)
        return ReferralFactory(referrer=referrer, referred=referred)

    def create_redeems(self) -> List[Redeem]:
        self.stdout.write('Creando redeems')
        coupon_type = CouponTypeFactory()
        return RedeemFactory(student=self.referral.referred, coupon__coupon_type=coupon_type)

    def create_reviews(self) -> List[Review]:
        self.stdout.write('Creando reviews')
        reviews = list()
        quantity = self.get_quantity()
        orders = self.get_sample(self.orders, quantity)
        for order in orders:
            reviews.append(ReviewFactory(activity=order.calendar.activity, author=order.student))

        return reviews
