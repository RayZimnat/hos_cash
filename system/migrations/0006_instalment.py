# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0005_auto_20150903_0502'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instalment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('instalment_date_due', models.DateField()),
                ('instalment_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('instalment_paid', models.BooleanField(default=False)),
                ('instalment_paid_date', models.DateField()),
                ('policy', models.ForeignKey(to='system.Policy')),
            ],
        ),
    ]
