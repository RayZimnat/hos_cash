# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0017_auto_20151108_0857'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='agent_commission',
            field=models.DecimalField(default=0.1, max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
    ]
