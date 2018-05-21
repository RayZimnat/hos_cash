# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_instalment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instalment',
            name='instalment_paid_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='insured',
            name='insured_employer',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
