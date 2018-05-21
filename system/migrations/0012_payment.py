# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0011_auto_20150922_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('payment_id', models.CharField(max_length=50, unique=True)),
                ('payment_date', models.DateField()),
                ('payment_method', models.CharField(max_length=20)),
                ('payment_value', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payment_proposal_number', models.CharField(max_length=50)),
                ('payment_matched', models.BooleanField(default=False)),
            ],
        ),
    ]
