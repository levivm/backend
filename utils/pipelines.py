from django.contrib.auth.models import User, Group
from guardian.shortcuts import assign_perm
from rest_framework.authtoken.models import Token

from students.models import Student


def get_username(details, *args, **kwargs):
    """
    Generate the username based on first and last name
    """
    first_name = details['first_name'].replace(' ', '').lower()
    last_name = details['last_name'].replace(' ', '').lower()
    username = '%s.%s' % (first_name, last_name)
    counter = User.objects.filter(username=username).count()

    if counter > 0:
        username += '%s' % (counter + 1)

    return {'username': username}

def create_profile(user, response, *args, **kwargs):
    """
    Create a student profile
    """
    profile = user.get_profile()
    if profile is None:
        gender = Student.FEMALE if response.get('gender') == 'female' else Student.MALE
        profile = Student.objects.create(user=user, gender=gender)

    return {'profile': profile}


def create_token(user, is_new, *args, **kwargs):
    """
    Create the auth token for the user
    """
    if is_new:
        Token.objects.create(user=user)


def assign_group(user, is_new, *args, **kwargs):
    """
    Assign the group to the user
    """
    if is_new:
        group = Group.objects.get(name='Students')
        user.groups.add(group)


def assign_permissions(user, is_new, profile, *args, **kwargs):
    """
    Assign permissions to the student
    """
    if is_new:
        assign_perm('students.change_student', user, profile)
