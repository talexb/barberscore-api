# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-17 16:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0110_auto_20160716_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='organization',
            new_name='district',
        ),
    ]