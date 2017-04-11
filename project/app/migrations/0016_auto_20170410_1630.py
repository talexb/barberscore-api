# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-10 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20170410_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='category',
            field=models.IntegerField(blank=True, choices=[(30, 'Music'), (40, 'Performance'), (50, 'Singing')], null=True),
        ),
        migrations.AlterField(
            model_name='score',
            name='category',
            field=models.IntegerField(choices=[(30, 'Music'), (40, 'Performance'), (50, 'Singing')]),
        ),
    ]