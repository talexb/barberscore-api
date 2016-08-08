# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-23 13:57
from __future__ import unicode_literals

import apps.api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0140_auto_20160723_0655'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestScore',
            fields=[
                ('contest_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Contest')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.contest',),
        ),
        migrations.CreateModel(
            name='PerformanceScore',
            fields=[
                ('performance_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Performance')),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('mus_points', models.IntegerField(blank=True, null=True)),
                ('prs_points', models.IntegerField(blank=True, null=True)),
                ('sng_points', models.IntegerField(blank=True, null=True)),
                ('total_points', models.IntegerField(blank=True, null=True)),
                ('mus_score', models.FloatField(blank=True, null=True)),
                ('prs_score', models.FloatField(blank=True, null=True)),
                ('sng_score', models.FloatField(blank=True, null=True)),
                ('total_score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.performance',),
        ),
        migrations.CreateModel(
            name='PerformerScore',
            fields=[
                ('performer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Performer')),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('mus_points', models.IntegerField(blank=True, null=True)),
                ('prs_points', models.IntegerField(blank=True, null=True)),
                ('sng_points', models.IntegerField(blank=True, null=True)),
                ('total_points', models.IntegerField(blank=True, null=True)),
                ('mus_score', models.FloatField(blank=True, null=True)),
                ('prs_score', models.FloatField(blank=True, null=True)),
                ('sng_score', models.FloatField(blank=True, null=True)),
                ('total_score', models.FloatField(blank=True, null=True)),
                ('csa_pdf', models.FileField(blank=True, help_text=b'\n            The historical PDF CSA.', null=True, upload_to=apps.api.models.generate_image_filename)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.performer',),
        ),
        migrations.CreateModel(
            name='SongScore',
            fields=[
                ('song_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Song')),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('mus_points', models.IntegerField(blank=True, null=True)),
                ('prs_points', models.IntegerField(blank=True, null=True)),
                ('sng_points', models.IntegerField(blank=True, null=True)),
                ('total_points', models.IntegerField(blank=True, null=True)),
                ('mus_score', models.FloatField(blank=True, null=True)),
                ('prs_score', models.FloatField(blank=True, null=True)),
                ('sng_score', models.FloatField(blank=True, null=True)),
                ('total_score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.song',),
        ),
        migrations.AddField(
            model_name='contestscore',
            name='champion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Performer'),
        ),
    ]