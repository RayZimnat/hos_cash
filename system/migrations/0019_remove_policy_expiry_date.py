# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0018_agent_agent_commission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='expiry_date',
        ),
    ]
