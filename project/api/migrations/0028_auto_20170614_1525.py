# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-14 22:25
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_auto_20170613_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (2, 'Listed'), (4, 'Opened'), (8, 'Closed'), (10, 'Verified'), (20, 'Started'), (30, 'Finished'), (50, 'Published')], default=0),
        ),
    ]
