# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-19 14:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0040_book_number_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='agent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='system.Agent'),
        ),
    ]
