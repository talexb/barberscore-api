# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-01 23:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0079_auto_20160630_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='performer',
            name='notification',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
