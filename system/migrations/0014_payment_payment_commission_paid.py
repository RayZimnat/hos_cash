# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0013_auto_20151002_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_commission_paid',
            field=models.BooleanField(default=False),
        ),
    ]
