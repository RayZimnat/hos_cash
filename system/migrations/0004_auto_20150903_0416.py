# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_plan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='dependant',
        ),
        migrations.AddField(
            model_name='dependant',
            name='plan',
            field=models.ForeignKey(to='system.Plan', default=1),
            preserve_default=False,
        ),
    ]
