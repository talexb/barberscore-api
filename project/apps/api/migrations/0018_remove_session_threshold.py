# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 21:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20160519_1444'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='threshold',
        ),
    ]