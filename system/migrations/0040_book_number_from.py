# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-19 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0039_auto_20160719_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='number_from',
            field=models.IntegerField(default=5, unique=True),
            preserve_default=False,
        ),
    ]