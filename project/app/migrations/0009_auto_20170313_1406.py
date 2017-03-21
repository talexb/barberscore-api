# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 21:06
from __future__ import unicode_literals

from django.db import migrations


def forwards(apps, schema_editor):
    Convention = apps.get_model('app', 'Convention')
    cs = Convention.objects.filter(
        year__lte=2016
    )
    for c in cs:
        ss = c.sessions.all()
        for s in ss:
            ts = s.contests.all()
            for t in ts:
                ns = t.contestants.all()
                for n in ns:
                    n.status = 90
                    n.save()
                t.status = 45
                t.save()
            ps = s.performers.all()
            for p in ps:
                fs = p.performances.all()
                for f in fs:
                    gs = f.songs.all()
                    for g in gs:
                        g.status = 90
                        g.save()
                    f.status = 90
                    f.save()
                p.status = 90
                p.save()
            s.status = 45
            s.save()
        c.status = 45
        c.save()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_contest_kind'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]