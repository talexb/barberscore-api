# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-09 04:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_auto_20160608_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='primary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_session', to='api.Contest'),
        ),
    ]