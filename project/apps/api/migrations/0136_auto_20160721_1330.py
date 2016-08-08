# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-21 20:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0135_auto_20160721_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestScore',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=200)),
                ('status', django_fsm.FSMIntegerField(choices=[(0, b'New'), (90, b'Published')], default=0)),
                ('champion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contestscore', to='api.Performer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='contest',
            name='contestscore',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contest', to='api.ContestScore'),
        ),
    ]