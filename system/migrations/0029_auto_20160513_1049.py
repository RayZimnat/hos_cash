# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-13 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0028_payment_payment_policy'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]