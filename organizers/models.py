from django.contrib.auth.models import User
from django.db import models

from utils.mixins import ImageOptimizable, AssignPermissionsMixin
from activities import constants as activities_constants

class Organizer(AssignPermissionsMixin, ImageOptimizable, models.Model):
    user = models.OneToOneField(User, related_name='organizer_profile')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True, blank=True, upload_to="avatars")
    telephone = models.CharField(max_length=100, blank=True)
    youtube_video_url = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=100, blank=True)
    headline = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0)
    verified_email = models.BooleanField(default=True)

    permissions = ('organizers.change_organizer',)


    def __str__(self):
        return '%s' % self.name

    def save(self, *args, **kwargs):
        if self.photo and not kwargs.get('update_fields'):
            self.photo.file.file = self.optimize(bytesio=self.photo.file.file, width=self.photo.width,
                                                 height=self.photo.height)

        super(Organizer, self).save(user=self.user, obj=self, *args, **kwargs)

    def get_activities_by_status(self, status=activities_constants.OPENED):
        activities = None
        if status == activities_constants.CLOSED:
            activities = self.activity_set.closed().all()
        elif status == activities_constants.UNPUBLISHED:
            activities = self.activity_set.unpublished().all()
        elif status == activities_constants.OPENED:
            activities = self.activity_set.opened().all()
        else:
            activities = self.activity_set.opened().all() | self.activity_set.closed().all()
        return activities



# Create your models here.
class Instructor(AssignPermissionsMixin, models.Model):
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    organizer = models.ForeignKey(Organizer, related_name="instructors", null=True)
    website = models.CharField(max_length=200, null=True, blank=True)

    permissions = ('organizers.change_instructor', 'organizers.delete_instructor')

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        super(Instructor, self).save(user=self.organizer.user, obj=self, *args, **kwargs)

    @classmethod
    def update_or_create(cls, instructors_data, organizer):
        instructors = []
        for ins in instructors_data:
            # Esto se usara en el futuro para asignar el instructor
            # al organizer
            # ins.update({'organizer':organizer})
            instructor = cls.objects.update_or_create(
                    id=ins.get('id', None),
                    defaults=ins)[0]
            instructors.append(instructor)

        return instructors


class OrganizerBankInfo(models.Model):
    BANKS = (
        ('agrario', 'BANCO AGRARIO'),
        ('av_villas', 'BANCO AV VILLAS'),
        ('bbva_colombia', 'BANCO BBVA S.A.'),
        ('caja_social', 'BANCO CAJA SOCIAL'),
        ('colpatria', 'BANCO COLPATRIA'),
        ('cooperativo_coopcentral', 'BANCO COOPERATIVO COOPCENTRAL'),
        ('corpbanca', 'BANCO CORPBANCA S.A.'),
        ('davivienda', 'BANCO DAVIVIENDA'),
        ('bogota', 'BANCO DE BOGOTÁ'),
        ('occidente', 'BANCO DE OCCIDENTE'),
        ('falabella', 'BANCO FALABELLA'),
        ('gnb_sudameris', 'BANCO GNB SUDAMERIS'),
        ('pichincha', 'BANCO PICHINCHA S.A.'),
        ('popular', 'BANCO POPULAR'),
        ('procredit', 'BANCO PROCREDIT'),
        ('bancolombia', 'BANCOLOMBIA'),
        ('bancoomeva', 'BANCOOMEVA S.A.'),
        ('citibank', 'CITIBANK'),
        ('helmbank', 'HELM BANK S.A.')
    )

    DOCUMENT_TYPES = (
        ('cc', 'Cédula de ciudadanía'),
        ('ce', 'Cédula de extranjería'),
        ('nit', 'NIT'),
        ('pp', 'Pasaporte'),
        ('de', 'Documento de identificación extranjero'),
    )

    ACCOUNT_TYPES = (
        ('ahorros', 'Cuenta de ahorros'),
        ('corriente', 'Cuenta corriente'),
    )


    NATURAL, JURIDICAL = range(1, 3)
    PERSON_TYPES = (
        (NATURAL, 'Natural'),
        (JURIDICAL, 'Jurídica'),
    )

    COMUN, MAJOR_CONTIBUTOR = range(1, 3)
    REGIMEN_TYPES = (
        (COMUN, 'Común'),
        (MAJOR_CONTIBUTOR, 'Gran Contribuyente'),
    )

    organizer = models.OneToOneField(Organizer, related_name='bank_info')
    beneficiary = models.CharField(max_length=255)
    bank = models.CharField(choices=BANKS, max_length=30)
    document_type = models.CharField(choices=DOCUMENT_TYPES, max_length=5)
    fiscal_address = models.CharField(max_length=255, blank=True)
    billing_telephone = models.CharField(max_length=100, blank=True)
    regimen = models.CharField(choices=REGIMEN_TYPES, max_length=20, blank=True)
    person_type = models.CharField(choices=PERSON_TYPES, max_length=10)
    document = models.CharField(max_length=100)
    account_type = models.CharField(choices=ACCOUNT_TYPES, max_length=10)
    account = models.CharField(max_length=255)

    @staticmethod
    def get_choices():
        return {
            'banks': [{'bank_id': k, 'bank_name': v} for k, v in OrganizerBankInfo.BANKS],
            'documents': [{'document_id': k, 'document_name': v} for k, v in OrganizerBankInfo.DOCUMENT_TYPES],
            'accounts': [{'account_id': k, 'account_name': v} for k, v in OrganizerBankInfo.ACCOUNT_TYPES],
            'person_type': [{'type_id': k, 'type_name': v} for k, v in OrganizerBankInfo.PERSON_TYPES],
            'regimen': [{'regimen_id': k, 'regimen_name': v} for k, v in OrganizerBankInfo.REGIMEN_TYPES],
        }
