# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('agent_code', models.CharField(unique=True, max_length=50)),
                ('agent_name', models.CharField(max_length=200)),
                ('agent_payment_method', models.CharField(max_length=100)),
                ('agent_account', models.CharField(verbose_name='Account number', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Dependant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('dependant_name', models.CharField(max_length=200)),
                ('dependant_id_number', models.CharField(max_length=50)),
                ('dependant_dob', models.DateField()),
                ('dependant_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Insured',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('insured_surname', models.CharField(max_length=200)),
                ('insured_name', models.CharField(max_length=200)),
                ('insured_gender', models.CharField(choices=[('m', 'Male'), ('f', 'Female')], default='m', max_length=2)),
                ('insured_id_number', models.CharField(max_length=20)),
                ('insured_dob', models.DateField()),
                ('insured_address', models.TextField()),
                ('insured_phone', models.CharField(max_length=200)),
                ('insured_employer', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('proposal_number', models.CharField(unique=True, max_length=50)),
                ('inception_date', models.DateField()),
                ('policy_expiry_date', models.DateField()),
                ('lapsed', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(to='system.Agent')),
                ('insured', models.ForeignKey(to='system.Insured')),
            ],
        ),
        migrations.AddField(
            model_name='dependant',
            name='policy',
            field=models.ForeignKey(to='system.Policy'),
        ),
    ]
