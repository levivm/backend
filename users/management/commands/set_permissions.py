from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from trulii.settings.constants import ORGANIZER_PERMISSIONS, STUDENT_PERMISSIONS, \
    OPERATIVE_PERMISSIONS


class Command(BaseCommand):
    help = "Create the user's groups and set the model permissions"

    def handle(self, *args, **options):
        self.set_permissions(*args, **options)

    def set_permissions(self, *args, **options):
        self.set_organizer_permissions()
        self.set_student_permissions()
        self.set_operative_permissions()
        self.set_marketing()

    def set_organizer_permissions(self):
        self.stdout.write("Organizer permissions...", ending="")
        organizers, created = Group.objects.get_or_create(name='Organizers')
        permissions = self.get_permissions_list(ORGANIZER_PERMISSIONS)
        self.add_permissions(organizers, permissions)
        self.stdout.write(self.style.SUCCESS(" DONE"))

    def set_student_permissions(self):
        self.stdout.write("Student permissions...", ending="")
        students, created = Group.objects.get_or_create(name='Students')
        permissions = self.get_permissions_list(STUDENT_PERMISSIONS)
        self.add_permissions(students, permissions)
        self.stdout.write(self.style.SUCCESS(" DONE"))

    def set_operative_permissions(self):
        self.stdout.write("Operative permissions...", ending="")
        operatives, created = Group.objects.get_or_create(name='Operatives')
        permissions = self.get_permissions_list(OPERATIVE_PERMISSIONS)
        self.add_permissions(operatives, permissions)
        self.stdout.write(self.style.SUCCESS(" DONE"))

    def set_marketing(self):
        self.stdout.write('Creating marketing group...', ending='')
        Group.objects.get_or_create(name='Marketing')
        self.stdout.write(self.style.SUCCESS(' DONE'))

    def add_permissions(self, group, permissions):
        group.permissions.add(*permissions)

    def get_permissions_list(self, permissions):
        return [Permission.objects.get_by_natural_key('%s_%s' % (codename, p['model']), p['app'],
                p['model']) for p in permissions for codename in p['codenames']]