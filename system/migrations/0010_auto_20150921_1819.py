# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0009_auto_20150910_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='dependant',
            name='dependant_gender',
            field=models.CharField(choices=[('m', 'Male'), ('f', 'Female')], max_length=2, default='m'),
        ),
        migrations.AddField(
            model_name='dependant',
            name='dependant_relationship',
            field=models.CharField(max_length=50, default='uncle'),
            preserve_default=False,
        ),
    ]
