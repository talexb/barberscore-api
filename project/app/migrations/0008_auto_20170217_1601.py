# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-18 00:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20170217_1554'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contestscore',
            name='champion',
        ),
        migrations.RemoveField(
            model_name='contestscore',
            name='contest_ptr',
        ),
        migrations.DeleteModel(
            name='ContestScore',
        ),
    ]