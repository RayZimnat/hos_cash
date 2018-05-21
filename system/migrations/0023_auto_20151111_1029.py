# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0022_auto_20151111_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dependant',
            name='dependant_monthly_premium',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12),
        ),
    ]
