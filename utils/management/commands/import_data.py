import csv
import datetime
import random
import string
from collections import namedtuple

import mock
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from guardian.shortcuts import assign_perm

from activities import constants as activities_constants
from activities.models import SubCategory
from activities.serializers import ActivitiesSerializer, CalendarSerializer
from balances.models import Balance
from locations.models import Location, City
from organizers.models import Organizer
from utils.serializers import UnixEpochDateField


class Command(BaseCommand):
    help = "Read files to load the data into the DB"
    organizers = dict()
    passwords = list()
    organizer_group = None
    activities = list()
    OrganizerPassword = namedtuple('OrganizerPassword', ['id', 'name', 'email', 'password'])

    def add_arguments(self, parser):
        parser.add_argument('-o', '--organizer-file',
                            default=None,
                            type=str,
                            help='CSV File with the organizer\'s information')
        parser.add_argument('-a', '--activity-file',
                            default=None,
                            type=str,
                            help='CSV File with the activities and calendar\'s information')

    def handle(self, *args, **options):
        try:
            self.organizer_group = Group.objects.get(name='Organizers')
        except Group.DoesNotExist:
            raise CommandError('The Organizers\' group does not exist')

        if options.get('organizer_file') is None or options.get('activity_file') is None:
            raise CommandError('Both files are required')

        with transaction.atomic():
            self.read_organizers(options['organizer_file'])
            self.create_organizers()

            self.read_activities(options['activity_file'])
            self.create_activities()
            
            self.output_passwords()

    def read_organizers(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                organizer_id, _, email, name, headline, bio, _, video, *_, special = row
                self.organizers[organizer_id] = {
                    'email': email,
                    'name': name.strip().title(),
                    'headline': headline.capitalize(),
                    'bio': bio.capitalize(),
                    'youtube_video_url': video,
                    'type': 'special' if slugify(special.lower()) == 'si' else 'normal',
                }

    def create_organizers(self):
        for id, data in self.organizers.items():
            self.stdout.write('Creating organizer "%s"...' % data['name'], ending='')
            email = data.pop('email')

            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR('DUPLICATED'))
                continue

            user = self.create_user(email, data['name'])
            user.groups.add(self.organizer_group)

            organizer = Organizer.objects.create(user=user, **data)
            self.organizers[id].update({'instance': organizer})

            assign_perm('organizers.change_organizer', user, organizer)
            Balance.objects.create(organizer=organizer)

            self.stdout.write(self.style.SUCCESS('DONE'))

    def create_user(self, email, name):
        password = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(6)])
        username = '.'.join(name.lower().split(' '))[:25]

        counter = User.objects.filter(username=username).count()
        if counter > 0:
            username += str(counter + 1)

        user = User.objects.create_user(username=username, email=email, password=password)
        self.passwords.append(
            self.OrganizerPassword(id=user.id, name=name, email=email, password=password))

        return user

    def read_activities(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                organizer_id = row[0]
                is_open = row[2]
                certification = row[4]
                level = row[5]
                category = row[6]
                subcategory = row[7]
                short_description = row[8]
                audience = row[9]
                goals = row[10]
                content = row[11]
                methodology = row[12]
                requirements = row[13]
                extra_info = row[14]
                open_calendar = row[20]
                closed_calendar = row[21]
                schedules = row[22]
                youtube_video_url = row[24]
                address = row[27]
                return_policy = row[28]
                title = row[29]
                post_enroll_message = row[30]

                levels = {
                    'principiante': activities_constants.LEVEL_P,
                    'intermedio': activities_constants.LEVEL_I,
                    'avanzado': activities_constants.LEVEL_A,
                    'no aplica': activities_constants.LEVEL_N,
                }

                organizer = self.organizers[str(organizer_id)]['instance']
                request = mock.MagicMock()
                request.user = organizer.user

                self.activities.append({
                    'organizer': organizer.id,
                    'is_open': True if slugify(is_open.lower()) == 'si' else False,
                    'certification': True if slugify(certification.lower()) == 'si' else False,
                    'level': levels[level.lower()],
                    'sub_category': SubCategory.objects.get(name=subcategory,
                                                            category__name=category).id,
                    'short_description': short_description,
                    'audience': audience,
                    'goals': goals,
                    'content': content,
                    'methodology': methodology,
                    'requirements': requirements,
                    'extra_info': extra_info,
                    'open_calendar': open_calendar,
                    'closed_calendar': closed_calendar,
                    'schedules': schedules,
                    'youtube_video_url': youtube_video_url,
                    'address': address,
                    'return_policy': return_policy,
                    'title': title.strip().title(),
                    'post_enroll_message': post_enroll_message,
                    'request': request,
                })

    def create_activities(self):
        for data in self.activities:
            self.stdout.write('Creating activity "%s"...' % data['title'], ending='')
            open_calendar = data.pop('open_calendar')
            closed_calendar = data.pop('closed_calendar')
            schedules = data.pop('schedules')
            address = data.pop('address')
            request = data.pop('request')

            serializer = ActivitiesSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            activity = serializer.save()

            location = Location.objects.create(
                address=address,
                city=City.objects.get(name='Bogotá'),
                point="POINT(-74.063644 4.624335)",
                organizer=activity.organizer)

            activity.location = location
            activity.save(update_fields=['location'])

            if activity.is_open:
                self.create_open_calendars(activity, open_calendar, schedules)
            else:
                self.create_closed_calendars(activity, closed_calendar, schedules)

            self.stdout.write(self.style.SUCCESS('DONE'))

    def create_open_calendars(self, activity, open_calendars, schedules):
        calendars = open_calendars.replace(' ', '').split(';')
        epoch = UnixEpochDateField()
        data = {
            'activity': activity.id,
            'available_capacity': 100,
            'initial_date': epoch.to_representation(datetime.datetime.max.date()),
            'schedules': schedules,
            'packages': [],
        }

        for calendar_data in calendars:
            quantity, price, type_ = calendar_data.split('-')
            data['packages'].append({
                'quantity': quantity,
                'price': price,
                'type': 1 if type_ == 'mes' else 2
            })

        serializer = CalendarSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def create_closed_calendars(self, activity, closed_calendars, schedules):
        calendars = closed_calendars.replace(' ', '').split(';')
        for calendar_data in calendars:
            epoch = UnixEpochDateField()
            date, capacity, price = calendar_data.split('-')
            data = {
                'activity': activity.id,
                'initial_date': epoch.to_representation(
                    datetime.datetime.strptime(date, '%d/%m/%Y').date()),
                'session_price': price,
                'available_capacity': capacity,
                'schedules': schedules,
            }
            serializer = CalendarSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def output_passwords(self):
        with open('passwords.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['User ID', 'Nombre', 'Email', 'Password'])
            for password in self.passwords:
                writer.writerow([password.id, password.name, password.email, password.password])
