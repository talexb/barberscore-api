# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-22 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0149_auto_20160922_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='phone',
            field=models.CharField(blank=True, default=b'', help_text=b'\n            The phone number of the resource.  Include country code.', max_length=25),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(blank=True, default=b'', help_text=b'\n            The phone number of the resource.  Include country code.', max_length=25),
        ),
    ]
