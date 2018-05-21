# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0010_auto_20150921_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='insured',
            name='insured_e_address',
            field=models.EmailField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='insured',
            name='insured_nationality',
            field=models.CharField(default='Zimbabwean', blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='insured',
            name='insured_occupation',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='policy',
            name='renewed',
            field=models.BooleanField(default=False),
        ),
    ]
