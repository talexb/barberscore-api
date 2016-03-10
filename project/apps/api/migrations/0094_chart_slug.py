# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-06 05:45
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0093_role_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, blank=True, editable=False, max_length=255, null=True, populate_from=b'name'),
        ),
    ]