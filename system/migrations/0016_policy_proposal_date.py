# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0015_policy_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='proposal_date',
            field=models.DateField(default=datetime.date(2015, 11, 8)),
        ),
    ]
