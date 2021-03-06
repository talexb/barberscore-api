# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 23:18
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_auto_20170630_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appearance',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (2, 'Scheduled'), (5, 'Verified'), (10, 'Started'), (20, 'Finished'), (30, 'Confirmed'), (40, 'Flagged'), (50, 'Scratched'), (60, 'Cleared'), (90, 'Published')], default=0),
        ),
    ]
