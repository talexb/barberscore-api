# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-03 06:45
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0067_auto_20160302_2154'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setlist',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=255, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, max_length=255, populate_from=b'name', unique=True)),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setlist', to='api.Catalog')),
                ('performer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setlist', to='api.Performer')),
            ],
        ),
        migrations.AlterField(
            model_name='singer',
            name='name',
            field=models.CharField(editable=False, max_length=255, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='setlist',
            unique_together=set([('performer', 'catalog')]),
        ),
    ]