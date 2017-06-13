# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 15:58
from __future__ import unicode_literals

import api.fields
from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_remove_chart_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='image',
            field=api.fields.CloudinaryRenameField(blank=True, max_length=255, null=True, verbose_name='raw'),
        ),
        migrations.AlterField(
            model_name='chart',
            name='holders',
            field=models.TextField(blank=True, default='(Unknown Copyright Holders)'),
        ),
        migrations.AlterField(
            model_name='chart',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(-10, 'Inactive'), (0, 'New'), (10, 'Active')], default=0),
        ),
    ]
