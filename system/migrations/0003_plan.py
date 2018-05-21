# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20150825_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('plan_name', models.CharField(max_length=50)),
                ('plan_premium', models.DecimalField(decimal_places=2, max_digits=12)),
                ('plan_cover_limit', models.DecimalField(decimal_places=2, max_digits=12)),
                ('plan_date_modified', models.DateTimeField(auto_now=True)),
                ('plan_modified_by', models.CharField(max_length=50)),
                ('dependant', models.ForeignKey(to='system.Dependant')),
            ],
        ),
    ]
