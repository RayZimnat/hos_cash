# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='id',
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.CharField(unique=True, serialize=False, max_length=50, primary_key=True),
        ),
    ]
