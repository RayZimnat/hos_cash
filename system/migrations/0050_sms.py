# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-12-23 15:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0049_auto_20161229_1252'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('party_type', models.CharField(max_length=20)),
                ('party_id', models.IntegerField()),
                ('phone_number', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('status', models.CharField(max_length=20)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
