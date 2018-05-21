# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-04 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0026_dependant_still_in_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayingAuthority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paying_authority_name', models.CharField(max_length=50, unique=True)),
                ('paying_contact_person', models.CharField(max_length=50)),
                ('paying_contact_number', models.CharField(max_length=50)),
                ('paying_cut_off_date', models.IntegerField(default=30)),
            ],
        ),
        migrations.AddField(
            model_name='policy',
            name='paying_authority',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='system.PayingAuthority'),
        ),
    ]