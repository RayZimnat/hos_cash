# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_auto_20150910_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instalment',
            name='instalment_paid_date',
            field=models.DateField(null=True),
        ),
    ]
