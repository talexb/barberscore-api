# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 11:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0183_auto_20160428_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='performer',
            name='soa',
            field=models.IntegerField(blank=True, help_text=b'\n            Starting Order of Appearance.', null=True),
        ),
    ]