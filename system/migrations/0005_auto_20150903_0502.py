# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_auto_20150903_0416'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plan',
            old_name='plan_premium',
            new_name='plan_adult_premium',
        ),
        migrations.AddField(
            model_name='plan',
            name='plan_minor_premium',
            field=models.DecimalField(decimal_places=2, max_digits=12, default=0),
            preserve_default=False,
        ),
    ]
