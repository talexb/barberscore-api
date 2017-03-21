# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-14 15:41
from __future__ import unicode_literals

from django.db import migrations


def forwards(apps, schema_editor):
    Award = apps.get_model('app', 'Award')
    awards = Award.objects.filter(
        season=None,
    ).order_by('nomen')
    for award in awards:
        if award.nomen == 'International Quartet Qualifier':
            award.season = 4
        elif award.nomen == 'International Chorus Qualifier':
            award.season = 3
        elif award.nomen.endswith('District Chorus Qualifier'):
            award.season = 4
        elif award.nomen.endswith('District Quartet Qualifier'):
            award.season = 3
        elif award.nomen.endswith('Chorus'):
            award.season = 3
        else:
            award.season = 4
        award.save()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20170316_1835'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]