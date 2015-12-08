from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from utils.models import CeleryTask


class Organizer(models.Model):
    user = models.OneToOneField(User, related_name='organizer_profile')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(null=True, blank=True, upload_to="avatars")
    telephone = models.CharField(max_length=100, blank=True)
    youtube_video_url = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=100, blank=True)
    headline = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    tasks = GenericRelation(CeleryTask)
    rating = models.FloatField(default=0)

    def __str__(self):
        return '%s' % self.user.username


# Create your models here.
class Instructor(models.Model):
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    photo = models.CharField(max_length=1000, verbose_name=_("Foto"), null=True, blank=True)
    organizer = models.ForeignKey(Organizer, related_name="instructors", null=True)
    website = models.CharField(max_length=200, null=True, blank=True)

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

    organizer = models.OneToOneField(Organizer, related_name='bank_info')
    beneficiary = models.CharField(max_length=255)
    bank = models.CharField(choices=BANKS, max_length=30)
    document_type = models.CharField(choices=DOCUMENT_TYPES, max_length=5)
    document = models.CharField(max_length=100)
    account_type = models.CharField(choices=ACCOUNT_TYPES, max_length=10)
    account = models.CharField(max_length=255)

    @staticmethod
    def get_choices():
        return {
            'banks': [{'bank_id': k, 'bank_name': v} for k, v in OrganizerBankInfo.BANKS],
            'documents': [{'document_id': k, 'document_name': v} for k, v in OrganizerBankInfo.DOCUMENT_TYPES],
            'accounts': [{'account_id': k, 'account_name': v} for k, v in OrganizerBankInfo.ACCOUNT_TYPES],
        }
