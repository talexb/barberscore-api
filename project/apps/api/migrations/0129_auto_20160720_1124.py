# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-20 18:24
from __future__ import unicode_literals

import apps.api.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0128_auto_20160718_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformerScore',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=255, unique=True)),
                ('status', django_fsm.FSMIntegerField(choices=[(0, b'New')], default=0)),
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
        ),
        migrations.AddField(
            model_name='performer',
            name='performer_score',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='performers', to='api.PerformerScore'),
        ),
    ]