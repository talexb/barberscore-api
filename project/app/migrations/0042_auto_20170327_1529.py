# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 22:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0041_auto_20170325_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='convention',
            name='close_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='convention',
            name='open_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]