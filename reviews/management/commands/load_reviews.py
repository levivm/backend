import json
import os
import random

import datetime
import pymongo
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create ghost reviews"

    def handle(self, *args, **options):
        today = datetime.date.today().toordinal()
        start_date = datetime.date(2016, 9, 27).toordinal()

        json_data = self.get_data()
        reviews_data = [{
            'id': random.choice(range(-500, -1)),
            'rating': 5.0,
            'comment': r['comment'],
            'reply': '',
            'activity': r['activity'],
            'author': {
                'id': random.choice(range(-100, -1)),
                'photo': None,
                'user': {
                    'first_name': r['first_name'],
                    'last_name': r['last_name'],
                    'email': r['email'],
                },
                'gender': r['gender'],
                'user_type': 'S',
                'birth_date': 862056007000.0,
                'telephone': '',
                'city': 1,
                'referrer_code': r['referrer_code'],
                'verified_email': True,
            },
            'created_at': datetime.date.fromordinal(
                random.choice(range(start_date, today))
            ).isoformat(),
            'reported': False,
            'read': True,
            'replied_at': None,
        }for r in json_data]

        client = pymongo.MongoClient(settings.MONGO_URL)
        db = client.get_database('trulii')
        reviews = db.get_collection('reviews')

        reviews.insert_many(reviews_data)

    def get_data(self):
        filepath = os.path.join(settings.PROJECT_PATH, '..', 'data', 'ghostreviews_data.json')
        with open(filepath, 'r') as jsonfile:
            data = json.load(jsonfile)

        return data
