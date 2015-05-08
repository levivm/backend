from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the user's groups and set the model permissions"

    def handle(self, *args, **options):
        self.set_organizer_permissions()
        self.set_student_permissions()

    def set_organizer_permissions(self):
        organizers, created = Group.objects.get_or_create(name='Organizers')
        organizers_permissions = {
            'activities': {
                'tags': [
                    'add'
                ],
                'activity': [
                    'add',
                    'change'
                ],
                'activityphoto': [
                    'add',
                    'delete'
                ],
                'chronogram': [
                    'add',
                    'change',
                    'delete'
                ],
                'session': [
                    'add',
                    'change',
                    'delete'
                ]
            },
            'locations': {
                'location': [
                    'add',
                    'change'
                ]
            },
            'organizers': {
                'organizer': [
                    'change'
                ],
                'instructor': [
                    'add',
                    'change',
                    'delete'
                ]
            }
        }

        permissions = self.get_permissions_list(organizers_permissions)
        self.add_permissions(organizers, permissions)

    def set_student_permissions(self):
        students, created = Group.objects.get_or_create(name='Students')
        students_permissions = {
            'activities': {
                'review': [
                    'add'
                ]
            },
            'orders': {
                'order': [
                    'add'
                ],
                'assistant': [
                    'add'
                ]
            },
            'students': {
                'student': [
                    'change'
                ]
            }
        }

        permissions = self.get_permissions_list(students_permissions)
        self.add_permissions(students, permissions)

    def add_permissions(self, group, permissions):
        group.permissions.add(*permissions)

    def get_permissions_list(self, permissions):
        permissions_list = []

        for app, values in permissions.items():
            for model, perms in values.items():
                for perm in perms:
                    permissions_list.append(Permission.objects.get_by_natural_key('%s_%s' % (perm, model), app, model))

        return permissions_list
