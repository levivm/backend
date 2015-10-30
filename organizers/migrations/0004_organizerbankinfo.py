# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0003_organizer_headline'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizerBankInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('beneficiary', models.CharField(max_length=255)),
                ('bank', models.CharField(max_length=30, choices=[('agrario', 'BANCO AGRARIO'), ('av_villas', 'BANCO AV VILLAS'), ('bbva_colombia', 'BANCO BBVA S.A.'), ('caja_social', 'BANCO CAJA SOCIAL'), ('colpatria', 'BANCO COLPATRIA'), ('cooperativo_coopcentral', 'BANCO COOPERATIVO COOPCENTRAL'), ('corpbanca', 'BANCO CORPBANCA S.A.'), ('davivienda', 'BANCO DAVIVIENDA'), ('bogota', 'BANCO DE BOGOTÁ'), ('occidente', 'BANCO DE OCCIDENTE'), ('falabella', 'BANCO FALABELLA'), ('gnb_sudameris', 'BANCO GNB SUDAMERIS'), ('pichincha', 'BANCO PICHINCHA S.A.'), ('popular', 'BANCO POPULAR'), ('procredit', 'BANCO PROCREDIT'), ('bancolombia', 'BANCOLOMBIA'), ('bancoomeva', 'BANCOOMEVA S.A.'), ('citibank', 'CITIBANK'), ('helmbank', 'HELM BANK S.A.')])),
                ('document_type', models.CharField(max_length=5, choices=[('cc', 'Cédula de ciudadanía'), ('ce', 'Cédula de extranjería'), ('nit', 'NIT'), ('pp', 'Pasaporte'), ('de', 'Documento de identificación extranjero')])),
                ('document', models.CharField(max_length=100)),
                ('account_type', models.CharField(max_length=10, choices=[('ahorros', 'Cuenta de ahorros'), ('corriente', 'Cuenta corriente')])),
                ('account', models.CharField(max_length=255)),
                ('organizer', models.OneToOneField(related_name='bank_info', to='organizers.Organizer')),
            ],
        ),
    ]
