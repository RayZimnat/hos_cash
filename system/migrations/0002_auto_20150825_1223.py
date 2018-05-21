# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='policy',
            old_name='policy_expiry_date',
            new_name='expiry_date',
        ),
    ]
