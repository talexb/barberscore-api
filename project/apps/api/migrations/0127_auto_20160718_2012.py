# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 03:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0126_auto_20160718_1939'),
    ]

    operations = [
        migrations.operations.RenameModel("Certification", "Judge")
    ]