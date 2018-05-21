# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0020_auto_20151110_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='dependant',
            name='dependant_monthly_premium',
            field=models.DecimalField(max_digits=12, default=0, decimal_places=2),
            preserve_default=False,
        ),
    ]
