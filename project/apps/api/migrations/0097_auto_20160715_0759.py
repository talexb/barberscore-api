# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-15 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0096_auto_20160714_2347'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='address1',
            field=models.CharField(blank=True, default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='address2',
            field=models.CharField(blank=True, default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='bhs_status',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='city',
            field=models.CharField(blank=True, default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='country',
            field=models.CharField(blank=True, default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='dues_thru',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='kind',
            field=models.IntegerField(choices=[(0, b'New'), (10, b'Member'), (20, b'Non-Member'), (30, b'Associate')], default=0),
        ),
        migrations.AddField(
            model_name='person',
            name='mon',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='postal_code',
            field=models.CharField(blank=True, default=b'', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='spouse',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='state',
            field=models.CharField(blank=True, default=b'', max_length=200),
        ),
    ]
