# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 20:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20170131_1230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='arranger',
        ),
    ]