# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-15 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0115_auto_20160315_0708'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='award',
            options={},
        ),
        migrations.AlterModelOptions(
            name='chapter',
            options={},
        ),
        migrations.AlterModelOptions(
            name='contest',
            options={},
        ),
        migrations.AlterModelOptions(
            name='contestant',
            options={},
        ),
        migrations.AlterModelOptions(
            name='convention',
            options={},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={},
        ),
        migrations.AlterModelOptions(
            name='judge',
            options={},
        ),
        migrations.AlterModelOptions(
            name='performance',
            options={},
        ),
        migrations.AlterModelOptions(
            name='performer',
            options={},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={},
        ),
        migrations.AlterModelOptions(
            name='round',
            options={},
        ),
        migrations.AlterModelOptions(
            name='score',
            options={},
        ),
        migrations.AlterModelOptions(
            name='session',
            options={},
        ),
        migrations.AlterModelOptions(
            name='song',
            options={},
        ),
        migrations.AlterModelOptions(
            name='venue',
            options={},
        ),
        migrations.AlterField(
            model_name='certification',
            name='name',
            field=models.CharField(editable=False, max_length=255, unique=True),
        ),
    ]