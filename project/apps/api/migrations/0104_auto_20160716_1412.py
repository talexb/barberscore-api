# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-16 21:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0103_auto_20160716_1409'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contest',
            old_name='champ',
            new_name='champion',
        ),
    ]
