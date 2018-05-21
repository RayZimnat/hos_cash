# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0021_dependant_dependant_monthly_premium'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dependant',
            name='dependant_monthly_premium',
            field=models.DecimalField(max_digits=12, decimal_places=2, default=0),
        ),
    ]
