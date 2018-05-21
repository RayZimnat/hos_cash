# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0019_remove_policy_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='payment_method',
            field=models.CharField(default='cash', max_length=20),
        ),
        migrations.AlterField(
            model_name='policy',
            name='inception_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
