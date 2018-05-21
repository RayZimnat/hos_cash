# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0014_payment_payment_commission_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='created_by',
            field=models.CharField(max_length=50, default='Someone'),
        ),
    ]
