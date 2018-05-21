# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0016_policy_proposal_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='proposal_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
